from asn.models import AsnDetailModel, AsnListModel
from binset.models import ListModel as BinSet
from stock.models import StockBinModel, StockListModel

from utils.test_helpers import AuthenticatedAPITestCase


class ReceivingOrderWorkflowTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_supplier()
        self.create_warehouse()
        self.create_goods_references()
        self.goods = self.create_goods()

    def create_order_with_details(self, goods_qty=5):
        header = self.client.post(
            '/asn/list/',
            {'supplier': 'Test Supplier', 'creater': 'Test Staff'},
            format='json',
        )
        self.assertEqual(header.status_code, 200, header.data)
        asn_code = header.data['asn_code']
        details = self.client.post(
            '/asn/detail/',
            {
                'asn_code': asn_code,
                'supplier': 'Test Supplier',
                'goods_code': [self.goods.goods_code],
                'goods_qty': [goods_qty],
            },
            format='json',
        )
        self.assertEqual(details.status_code, 200, details.data)
        return AsnListModel.objects.get(openid=self.openid, asn_code=asn_code)

    def test_create_receiving_order_updates_totals_and_inbound_stock(self):
        order = self.create_order_with_details(goods_qty=5)
        order.refresh_from_db()
        detail = AsnDetailModel.objects.get(openid=self.openid, asn_code=order.asn_code, is_delete=False)
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)

        self.assertEqual(order.asn_status, 1)
        self.assertEqual(order.total_weight, 5)
        self.assertEqual(order.total_volume, 0.005)
        self.assertEqual(order.total_cost, 12.5)
        self.assertEqual(detail.goods_qty, 5)
        self.assertEqual(stock.goods_qty, 5)
        self.assertEqual(stock.asn_stock, 5)

    def test_receiving_workflow_preload_presort_and_sort_updates_stock(self):
        order = self.create_order_with_details(goods_qty=5)

        preload = self.client.post('/asn/preload/{}/'.format(order.id), {}, format='json')
        self.assertEqual(preload.status_code, 200, preload.data)
        presort = self.client.post('/asn/presort/{}/'.format(order.id), {}, format='json')
        self.assertEqual(presort.status_code, 200, presort.data)
        sorted_response = self.client.post(
            '/asn/sorted/{}/'.format(order.id),
            {
                'asn_code': order.asn_code,
                'supplier': 'Test Supplier',
                'goodsData': [{'goods_code': self.goods.goods_code, 'goods_actual_qty': 4}],
            },
            format='json',
        )

        self.assertEqual(sorted_response.status_code, 200, sorted_response.data)
        order.refresh_from_db()
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)
        detail = AsnDetailModel.objects.get(openid=self.openid, asn_code=order.asn_code, is_delete=False)
        self.assertEqual(order.asn_status, 4)
        self.assertEqual(detail.asn_status, 4)
        self.assertEqual(detail.goods_actual_qty, 4)
        self.assertEqual(detail.goods_shortage_qty, 1)
        self.assertEqual(stock.goods_qty, 4)
        self.assertEqual(stock.asn_stock, 0)
        self.assertEqual(stock.pre_load_stock, 0)
        self.assertEqual(stock.pre_sort_stock, 0)
        self.assertEqual(stock.sorted_stock, 4)

    def test_move_sorted_goods_to_bin_updates_available_inventory(self):
        order = self.create_order_with_details(goods_qty=5)
        self.client.post('/asn/preload/{}/'.format(order.id), {}, format='json')
        self.client.post('/asn/presort/{}/'.format(order.id), {}, format='json')
        self.client.post(
            '/asn/sorted/{}/'.format(order.id),
            {
                'asn_code': order.asn_code,
                'supplier': 'Test Supplier',
                'goodsData': [{'goods_code': self.goods.goods_code, 'goods_actual_qty': 4}],
            },
            format='json',
        )
        detail = AsnDetailModel.objects.get(openid=self.openid, asn_code=order.asn_code, is_delete=False)
        binset = BinSet.objects.create(
            bin_name='Receiving Bin',
            bin_size='Medium',
            bin_property='Normal',
            creater='Test Staff',
            bar_code='receiving-bin',
            openid=self.openid,
        )

        response = self.client.post(
            '/asn/movetobin/{}/'.format(detail.id),
            {'asn_code': order.asn_code, 'goods_code': self.goods.goods_code, 'qty': 4, 'bin_name': binset.bin_name},
            format='json',
        )

        self.assertEqual(response.status_code, 200, response.data)
        detail.refresh_from_db()
        order.refresh_from_db()
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)
        bin_stock = StockBinModel.objects.get(openid=self.openid, bin_name=binset.bin_name)
        self.assertEqual(detail.sorted_qty, 4)
        self.assertEqual(detail.asn_status, 5)
        self.assertEqual(order.asn_status, 5)
        self.assertEqual(stock.sorted_stock, 0)
        self.assertEqual(stock.onhand_stock, 4)
        self.assertEqual(stock.can_order_stock, 4)
        self.assertEqual(bin_stock.goods_qty, 4)

    def test_delete_unconfirmed_receiving_order_reverses_stock_reservation(self):
        order = self.create_order_with_details(goods_qty=5)
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)

        response = self.client.delete('/asn/list/{}/'.format(order.id))

        self.assertEqual(response.status_code, 200, response.data)
        order.refresh_from_db()
        stock.refresh_from_db()
        self.assertTrue(order.is_delete)
        self.assertEqual(stock.goods_qty, 0)
        self.assertEqual(stock.asn_stock, 0)
        self.assertFalse(
            AsnDetailModel.objects.filter(openid=self.openid, asn_code=order.asn_code, is_delete=False).exists()
        )