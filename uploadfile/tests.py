import csv
from io import StringIO

from django.core.files.uploadedfile import SimpleUploadedFile

from goods.models import ListModel as Goods
from goodsbrand.models import ListModel as GoodsBrand
from goodsclass.models import ListModel as GoodsClass
from goodscolor.models import ListModel as GoodsColor
from goodsorigin.models import ListModel as GoodsOrigin
from goodsshape.models import ListModel as GoodsShape
from goodsspecs.models import ListModel as GoodsSpecs
from goodsunit.models import ListModel as GoodsUnit
from capital.models import ListModel as Capital
from customer.models import ListModel as Customer
from payment.models import TransportationFeeListModel as Freight
from scanner.models import ListModel as Scanner
from supplier.models import ListModel as Supplier
from utils.test_helpers import AuthenticatedAPITestCase


class GoodsImportWorkflowTests(AuthenticatedAPITestCase):
    def upload_csv(self, endpoint, headers, row, name):
        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        writer.writerow(row)
        upload = SimpleUploadedFile(
            '{}.csv'.format(name),
            csv_file.getvalue().encode('utf-8'),
            content_type='text/csv',
        )
        return self.client.post(
            '/uploadfile/{}/'.format(endpoint),
            {'file': upload},
            format='multipart',
        )

    def test_csv_import_creates_goods_and_reference_records(self):
        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerow([
            'Goods Code',
            'Goods Description',
            'Goods Supplier',
            'Goods Weight',
            'Goods Wide',
            'Goods Depth',
            'Goods Height',
            'Unit Volume',
            'Goods Unit',
            'Goods Class',
            'Goods Brand',
            'Goods Color',
            'Goods Shape',
            'Goods Specs',
            'Goods Origin',
            'Goods Cost',
            'Goods Price',
            'Creater',
            'Create Time',
            'Update Time',
        ])
        writer.writerow([
            'CSV-001', 'Imported product', 'Imported supplier', 1000, 100, 200, 300, 0.006,
            'Each', 'Imported class', 'Imported brand', 'Blue', 'Box', 'Large', 'Local',
            2.5, 4, 'Test Staff', '', '',
        ])
        upload = SimpleUploadedFile(
            'goods.csv',
            csv_file.getvalue().encode('utf-8'),
            content_type='text/csv',
        )

        response = self.client.post(
            '/uploadfile/goodslistfile/',
            {'file': upload},
            format='multipart',
        )

        self.assertEqual(response.status_code, 200, getattr(response, 'data', None))
        imported = Goods.objects.get(openid=self.openid, goods_code='CSV-001')
        self.assertEqual(imported.goods_desc, 'Imported product')
        self.assertTrue(Supplier.objects.filter(openid=self.openid, supplier_name='Imported supplier').exists())
        self.assertTrue(GoodsUnit.objects.filter(openid=self.openid, goods_unit='Each').exists())
        self.assertTrue(GoodsClass.objects.filter(openid=self.openid, goods_class='Imported class').exists())
        self.assertTrue(GoodsBrand.objects.filter(openid=self.openid, goods_brand='Imported brand').exists())
        self.assertTrue(GoodsColor.objects.filter(openid=self.openid, goods_color='Blue').exists())
        self.assertTrue(GoodsShape.objects.filter(openid=self.openid, goods_shape='Box').exists())
        self.assertTrue(GoodsSpecs.objects.filter(openid=self.openid, goods_specs='Large').exists())
        self.assertTrue(GoodsOrigin.objects.filter(openid=self.openid, goods_origin='Local').exists())
        self.assertTrue(Scanner.objects.filter(openid=self.openid, mode='GOODS', code='CSV-001').exists())

    def test_goods_append_import_is_idempotent_by_goods_code(self):
        headers = [
            'Goods Code', 'Goods Description', 'Goods Supplier', 'Goods Weight', 'Goods Wide',
            'Goods Depth', 'Goods Height', 'Unit Volume', 'Goods Unit', 'Goods Class',
            'Goods Brand', 'Goods Color', 'Goods Shape', 'Goods Specs', 'Goods Origin',
            'Goods Cost', 'Goods Price',
        ]
        row = [
            'APPEND-001', 'Append product', 'Append Supplier', 1000, 100, 200, 300, 0.006,
            'Each', 'Class', 'Brand', 'Blue', 'Box', 'Large', 'Local', 2.5, 4,
        ]

        first = self.upload_csv('goodslistfileadd', headers, row, 'goods-add-first')
        second = self.upload_csv('goodslistfileadd', headers, row, 'goods-add-second')

        self.assertEqual(first.status_code, 200, getattr(first, 'data', None))
        self.assertEqual(second.status_code, 200, getattr(second, 'data', None))
        self.assertEqual(Goods.objects.filter(openid=self.openid, goods_code='APPEND-001').count(), 1)

    def test_supplier_and_customer_imports_replace_or_append_tenant_data(self):
        old_supplier = self.create_supplier(name='Old Supplier')
        supplier_headers = [
            'Supplier Name', 'Supplier City', 'Supplier Address',
            'Supplier Contact', 'Supplier Manager', 'Supplier Level',
        ]
        supplier_row = ['CSV Supplier', 'City', 'Address', 1234567, 'Manager', 2]

        replaced_supplier = self.upload_csv('supplierfile', supplier_headers, supplier_row, 'supplier')

        self.assertEqual(replaced_supplier.status_code, 200, getattr(replaced_supplier, 'data', None))
        self.assertFalse(Supplier.objects.filter(id=old_supplier.id).exists())
        self.assertTrue(Supplier.objects.filter(openid=self.openid, supplier_name='CSV Supplier').exists())

        appended_supplier = self.upload_csv('supplierfileadd', supplier_headers, supplier_row, 'supplier-add')

        self.assertEqual(appended_supplier.status_code, 200, getattr(appended_supplier, 'data', None))
        self.assertEqual(Supplier.objects.filter(openid=self.openid, supplier_name='CSV Supplier').count(), 1)

        old_customer = self.create_customer(name='Old Customer')
        customer_headers = [
            'Customer Name', 'Customer City', 'Customer Address',
            'Customer Contact', 'Customer Manager', 'Customer Level',
        ]
        customer_row = ['CSV Customer', 'City', 'Address', 1234567, 'Manager', 2]

        replaced_customer = self.upload_csv('customerfile', customer_headers, customer_row, 'customer')

        self.assertEqual(replaced_customer.status_code, 200, getattr(replaced_customer, 'data', None))
        self.assertFalse(Customer.objects.filter(id=old_customer.id).exists())
        self.assertTrue(Customer.objects.filter(openid=self.openid, customer_name='CSV Customer').exists())

        appended_customer = self.upload_csv('customerfileadd', customer_headers, customer_row, 'customer-add')

        self.assertEqual(appended_customer.status_code, 200, getattr(appended_customer, 'data', None))
        self.assertEqual(Customer.objects.filter(openid=self.openid, customer_name='CSV Customer').count(), 1)

    def test_capital_and_freight_imports_replace_or_append_records(self):
        Capital.objects.create(
            capital_name='Old Capital',
            capital_qty=1,
            capital_cost=1,
            creater='Test Staff',
            openid=self.openid,
        )
        capital_headers = ['Capital Name', 'Capital Qty', 'Capital Cost']
        capital_row = ['CSV Capital', 3, 12.5]

        replaced_capital = self.upload_csv('capitalfile', capital_headers, capital_row, 'capital')

        self.assertEqual(replaced_capital.status_code, 200, getattr(replaced_capital, 'data', None))
        self.assertFalse(Capital.objects.filter(openid=self.openid, capital_name='Old Capital').exists())
        self.assertTrue(Capital.objects.filter(openid=self.openid, capital_name='CSV Capital').exists())

        appended_capital = self.upload_csv('capitalfileadd', capital_headers, capital_row, 'capital-add')

        self.assertEqual(appended_capital.status_code, 200, getattr(appended_capital, 'data', None))
        self.assertEqual(Capital.objects.filter(openid=self.openid, capital_name='CSV Capital').count(), 1)

        freight_headers = [
            'Send City', 'Receiver City', 'Weight Fee', 'Volume Fee',
            'Min Payment', 'Transportation Supplier',
        ]
        freight_row = ['Origin', 'Destination', 1.5, 2.5, 3, 'Carrier']

        replaced_freight = self.upload_csv('freightfile', freight_headers, freight_row, 'freight')

        self.assertEqual(replaced_freight.status_code, 200, getattr(replaced_freight, 'data', None))
        self.assertTrue(
            Freight.objects.filter(
                openid=self.openid,
                send_city='Origin',
                receiver_city='Destination',
                transportation_supplier='Carrier',
            ).exists()
        )

        appended_freight = self.upload_csv('freightfileadd', freight_headers, freight_row, 'freight-add')

        self.assertEqual(appended_freight.status_code, 200, getattr(appended_freight, 'data', None))
        self.assertEqual(
            Freight.objects.filter(
                openid=self.openid,
                send_city='Origin',
                receiver_city='Destination',
                transportation_supplier='Carrier',
            ).count(),
            1,
        )