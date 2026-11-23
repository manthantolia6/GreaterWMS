from goods.models import ListModel as Goods
from scanner.models import ListModel as Scanner

from utils.test_helpers import AuthenticatedAPITestCase


class GoodsApiTests(AuthenticatedAPITestCase):
    endpoint = '/goods/'

    def setUp(self):
        super().setUp()
        self.create_goods_references()

    def goods_payload(self, code='API-GOODS-001'):
        return {
            'goods_code': code,
            'goods_desc': 'API-created product',
            'goods_supplier': 'Test Supplier',
            'goods_weight': 1000,
            'goods_w': 100,
            'goods_d': 200,
            'goods_h': 300,
            'unit_volume': 0,
            'goods_unit': 'Each',
            'goods_class': 'Test Class',
            'goods_brand': 'Test Brand',
            'goods_color': 'Test Color',
            'goods_shape': 'Test Shape',
            'goods_specs': 'Test Specs',
            'goods_origin': 'Test Origin',
            'safety_stock': 0,
            'goods_cost': 2.5,
            'goods_price': 4,
            'creater': 'Test Staff',
            'bar_code': 'ignored-by-create-view',
        }

    def test_create_computes_volume_and_creates_scanner_code(self):
        response = self.client.post(self.endpoint, self.goods_payload(), format='json')

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['unit_volume'], 0.006)
        goods = Goods.objects.get(openid=self.openid, goods_code='API-GOODS-001')
        self.assertEqual(goods.bar_code, response.data['bar_code'])
        self.assertTrue(
            Scanner.objects.filter(
                openid=self.openid,
                mode='GOODS',
                code=goods.goods_code,
                bar_code=goods.bar_code,
            ).exists()
        )

    def test_duplicate_goods_code_is_rejected(self):
        self.create_goods(code='API-GOODS-001')

        response = self.client.post(self.endpoint, self.goods_payload(), format='json')

        self.assertGreaterEqual(response.data['status_code'], 400)
        self.assertEqual(Goods.objects.filter(openid=self.openid, goods_code='API-GOODS-001').count(), 1)

    def test_goods_list_is_scoped_to_authenticated_tenant(self):
        own_goods = self.create_goods()
        Goods.objects.create(
            goods_code='OTHER-GOODS',
            goods_desc='Other tenant product',
            goods_supplier='Other Supplier',
            goods_weight=1,
            goods_w=1,
            goods_d=1,
            goods_h=1,
            unit_volume=0,
            goods_unit='Each',
            goods_class='Test Class',
            goods_brand='Test Brand',
            goods_color='Test Color',
            goods_shape='Test Shape',
            goods_specs='Test Specs',
            goods_origin='Test Origin',
            safety_stock=0,
            goods_cost=1,
            goods_price=1,
            creater='Other',
            bar_code='other-barcode',
            openid='other-openid',
        )

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['goods_code'] for item in response.data['results']],
            [own_goods.goods_code],
        )