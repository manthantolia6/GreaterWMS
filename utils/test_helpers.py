from django.test import TestCase
from rest_framework.test import APIClient

from customer.models import ListModel as Customer
from goods.models import ListModel as Goods
from goodsbrand.models import ListModel as GoodsBrand
from goodsclass.models import ListModel as GoodsClass
from goodscolor.models import ListModel as GoodsColor
from goodsorigin.models import ListModel as GoodsOrigin
from goodsshape.models import ListModel as GoodsShape
from goodsspecs.models import ListModel as GoodsSpecs
from goodsunit.models import ListModel as GoodsUnit
from staff.models import ListModel as Staff
from supplier.models import ListModel as Supplier
from userprofile.models import Users
from warehouse.models import ListModel as Warehouse


class AuthenticatedAPITestCase(TestCase):
    openid = 'test-openid'

    def setUp(self):
        self.user = Users.objects.create(
            name='Test User',
            openid=self.openid,
            appid='test-appid',
            t_code='test-transaction',
            ip='127.0.0.1',
        )
        self.staff = Staff.objects.create(
            staff_name='Test Staff',
            staff_type='Admin',
            openid=self.openid,
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_TOKEN=self.openid,
            HTTP_OPERATOR=str(self.staff.id),
        )

    def create_supplier(self, name='Test Supplier', city='Origin'):
        return Supplier.objects.create(
            supplier_name=name,
            supplier_city=city,
            supplier_address='Supplier address',
            supplier_contact='123456789',
            supplier_manager='Supplier Manager',
            supplier_level=1,
            creater='Test Staff',
            openid=self.openid,
        )

    def create_customer(self, name='Test Customer', city='Destination'):
        return Customer.objects.create(
            customer_name=name,
            customer_city=city,
            customer_address='Customer address',
            customer_contact='123456789',
            customer_manager='Customer Manager',
            customer_level=1,
            creater='Test Staff',
            openid=self.openid,
        )

    def create_warehouse(self, name='Test Warehouse', city='Origin'):
        return Warehouse.objects.create(
            warehouse_name=name,
            warehouse_city=city,
            warehouse_address='Warehouse address',
            warehouse_contact='123456789',
            warehouse_manager='Warehouse Manager',
            creater='Test Staff',
            openid=self.openid,
        )

    def create_goods_references(self):
        self.create_supplier()
        GoodsUnit.objects.create(goods_unit='Each', creater='Test Staff', openid=self.openid)
        GoodsClass.objects.create(goods_class='Test Class', creater='Test Staff', openid=self.openid)
        GoodsBrand.objects.create(goods_brand='Test Brand', creater='Test Staff', openid=self.openid)
        GoodsColor.objects.create(goods_color='Test Color', creater='Test Staff', openid=self.openid)
        GoodsShape.objects.create(goods_shape='Test Shape', creater='Test Staff', openid=self.openid)
        GoodsSpecs.objects.create(goods_specs='Test Specs', creater='Test Staff', openid=self.openid)
        GoodsOrigin.objects.create(goods_origin='Test Origin', creater='Test Staff', openid=self.openid)

    def create_goods(self, code='TEST-001', weight=1000, cost=2.5, price=4.0):
        return Goods.objects.create(
            goods_code=code,
            goods_desc='Test product',
            goods_supplier='Test Supplier',
            goods_weight=weight,
            goods_w=100,
            goods_d=100,
            goods_h=100,
            unit_volume=0.001,
            goods_unit='Each',
            goods_class='Test Class',
            goods_brand='Test Brand',
            goods_color='Test Color',
            goods_shape='Test Shape',
            goods_specs='Test Specs',
            goods_origin='Test Origin',
            safety_stock=0,
            goods_cost=cost,
            goods_price=price,
            creater='Test Staff',
            bar_code='barcode-{}'.format(code),
            openid=self.openid,
        )
