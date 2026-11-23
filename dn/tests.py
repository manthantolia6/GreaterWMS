from dn.models import DnDetailModel, DnListModel
from dn.models import PickingListModel
from driver.models import DispatchListModel, ListModel as Driver
from stock.models import StockBinModel, StockListModel

from utils.test_helpers import AuthenticatedAPITestCase


class DeliveryOrderWorkflowTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_customer()
        self.create_warehouse()
        self.create_goods_references()
        self.goods = self.create_goods()

    def create_order_with_details(self, goods_qty=5):
        header = self.client.post(
            '/dn/list/',
            {'customer': 'Test Customer', 'creater': 'Test Staff'},
            format='json',
        )
        self.assertEqual(header.status_code, 200, header.data)
        dn_code = header.data['dn_code']
        details = self.client.post(
            '/dn/detail/',
            {
                'dn_code': dn_code,
                'customer': 'Test Customer',
                'goods_code': [self.goods.goods_code],
                'goods_qty': [goods_qty],
            },
            format='json',
        )
        self.assertEqual(details.status_code, 200, details.data)
        return DnListModel.objects.get(openid=self.openid, dn_code=dn_code)

    def test_create_delivery_order_updates_order_totals_and_reserved_stock(self):
        order = self.create_order_with_details(goods_qty=5)

        detail = DnDetailModel.objects.get(openid=self.openid, dn_code=order.dn_code, is_delete=False)
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)
        order.refresh_from_db()

        self.assertEqual(order.dn_status, 1)
        self.assertEqual(order.total_weight, 5)
        self.assertEqual(order.total_volume, 0.005)
        self.assertEqual(order.total_cost, 20)
        self.assertEqual(detail.goods_qty, 5)
        self.assertEqual(stock.dn_stock, 5)

    def test_confirm_preorder_moves_reserved_stock_to_ordered(self):
        order = self.create_order_with_details(goods_qty=5)
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)
        stock.onhand_stock = 10
        stock.can_order_stock = 10
        stock.save()

        response = self.client.post('/dn/neworder/{}/'.format(order.id), {}, format='json')

        self.assertEqual(response.status_code, 200, response.data)
        order.refresh_from_db()
        stock.refresh_from_db()
        detail = DnDetailModel.objects.get(openid=self.openid, dn_code=order.dn_code, is_delete=False)
        self.assertEqual(order.dn_status, 2)
        self.assertEqual(detail.dn_status, 2)
        self.assertEqual(stock.can_order_stock, 5)
        self.assertEqual(stock.ordered_stock, 5)
        self.assertEqual(stock.dn_stock, 0)

    def test_order_release_creates_bin_picking_work(self):
        order = self.create_order_with_details(goods_qty=5)
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)
        stock.onhand_stock = 5
        stock.can_order_stock = 5
        stock.save()
        self.client.post('/dn/neworder/{}/'.format(order.id), {}, format='json')
        stock.refresh_from_db()
        StockBinModel.objects.create(
            bin_name='Pick Bin',
            goods_code=self.goods.goods_code,
            goods_desc=self.goods.goods_desc,
            goods_qty=5,
            bin_size='Medium',
            bin_property='Normal',
            t_code='pick-bin-transaction',
            openid=self.openid,
            create_time=order.create_time,
        )

        response = self.client.post('/dn/orderrelease/', {}, format='json')

        self.assertEqual(response.status_code, 200, response.data)
        order.refresh_from_db()
        stock.refresh_from_db()
        detail = DnDetailModel.objects.get(openid=self.openid, dn_code=order.dn_code, is_delete=False)
        picking = PickingListModel.objects.get(openid=self.openid, dn_code=order.dn_code)
        bin_stock = StockBinModel.objects.get(openid=self.openid, t_code='pick-bin-transaction')
        self.assertEqual(order.dn_status, 3)
        self.assertEqual(detail.dn_status, 3)
        self.assertEqual(detail.pick_qty, 5)
        self.assertEqual(picking.pick_qty, 5)
        self.assertEqual(stock.pick_stock, 5)
        self.assertEqual(bin_stock.pick_qty, 5)

    def test_picking_dispatch_and_pod_complete_outbound_order(self):
        order = self.create_order_with_details(goods_qty=5)
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)
        stock.goods_qty = 5
        stock.onhand_stock = 5
        stock.can_order_stock = 5
        stock.save()
        self.client.post('/dn/neworder/{}/'.format(order.id), {}, format='json')
        StockBinModel.objects.create(
            bin_name='Outbound Bin',
            goods_code=self.goods.goods_code,
            goods_desc=self.goods.goods_desc,
            goods_qty=5,
            bin_size='Medium',
            bin_property='Normal',
            t_code='outbound-bin-transaction',
            openid=self.openid,
            create_time=order.create_time,
        )
        release = self.client.post('/dn/orderrelease/', {}, format='json')
        self.assertEqual(release.status_code, 200, release.data)
        picking = PickingListModel.objects.get(openid=self.openid, dn_code=order.dn_code)

        picked = self.client.post(
            '/dn/picked/{}/'.format(order.id),
            {
                'dn_code': order.dn_code,
                'customer': 'Test Customer',
                'goodsData': [{
                    'goods_code': self.goods.goods_code,
                    't_code': picking.t_code,
                    'pick_qty': 5,
                }],
            },
            format='json',
        )
        self.assertEqual(picked.status_code, 200, picked.data)
        order.refresh_from_db()
        picking.refresh_from_db()
        self.assertEqual(order.dn_status, 4)
        self.assertEqual(picking.picked_qty, 5)
        self.assertEqual(picking.picking_status, 1)

        Driver.objects.create(
            driver_name='Test Driver',
            license_plate='TEST-123',
            contact='5550123',
            creater='Test Staff',
            openid=self.openid,
        )
        dispatched = self.client.post(
            '/dn/dispatch/{}/'.format(order.id),
            {'dn_code': order.dn_code, 'driver': 'Test Driver'},
            format='json',
        )
        self.assertEqual(dispatched.status_code, 200, dispatched.data)
        order.refresh_from_db()
        self.assertEqual(order.dn_status, 5)
        self.assertTrue(
            DispatchListModel.objects.filter(openid=self.openid, dn_code=order.dn_code).exists()
        )

        pod = self.client.post(
            '/dn/pod/{}/'.format(order.id),
            {
                'dn_code': order.dn_code,
                'goodsData': [{
                    'goods_code': self.goods.goods_code,
                    'intransit_qty': 5,
                    'delivery_damage_qty': 0,
                }],
            },
            format='json',
        )
        self.assertEqual(pod.status_code, 200, pod.data)
        order.refresh_from_db()
        detail = DnDetailModel.objects.get(openid=self.openid, dn_code=order.dn_code, is_delete=False)
        self.assertEqual(order.dn_status, 6)
        self.assertEqual(detail.dn_status, 6)
        self.assertEqual(detail.delivery_actual_qty, 5)
        self.assertEqual(detail.delivery_shortage_qty, 0)

    def test_delete_unconfirmed_order_releases_reserved_stock(self):
        order = self.create_order_with_details(goods_qty=5)
        stock = StockListModel.objects.get(openid=self.openid, goods_code=self.goods.goods_code)

        response = self.client.delete('/dn/list/{}/'.format(order.id))

        self.assertEqual(response.status_code, 200, response.data)
        order.refresh_from_db()
        stock.refresh_from_db()
        self.assertTrue(order.is_delete)
        self.assertEqual(stock.dn_stock, 0)
        self.assertFalse(
            DnDetailModel.objects.filter(openid=self.openid, dn_code=order.dn_code, is_delete=False).exists()
        )

    def test_detail_creation_rejects_unknown_goods_without_reserving_stock(self):
        header = self.client.post(
            '/dn/list/',
            {'customer': 'Test Customer', 'creater': 'Test Staff'},
            format='json',
        )
        self.assertEqual(header.status_code, 200, header.data)

        response = self.client.post(
            '/dn/detail/',
            {
                'dn_code': header.data['dn_code'],
                'customer': 'Test Customer',
                'goods_code': ['UNKNOWN-GOODS'],
                'goods_qty': [2],
            },
            format='json',
        )

        self.assertGreaterEqual(response.data['status_code'], 400)
        self.assertFalse(DnDetailModel.objects.filter(dn_code=header.data['dn_code']).exists())
        self.assertFalse(StockListModel.objects.filter(goods_code='UNKNOWN-GOODS').exists())