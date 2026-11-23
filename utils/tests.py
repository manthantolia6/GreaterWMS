from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase
from types import SimpleNamespace
from unittest.mock import patch
from rest_framework.exceptions import APIException
from userprofile.models import Users
from rest_framework.test import APIClient

from utils.datasolve import (
    appid_validate,
    asn_data_validate,
    data_validate,
    dn_data_validate,
    is_number,
    openid_validate,
    qty_0_data_validate,
    qty_data_validate,
    secret_bar_code,
    sumOfList,
    transportation_calculate,
    verify_bar_code,
)
from utils.test_helpers import AuthenticatedAPITestCase
from greaterwms.test_runner import IsolatedDatabaseTestRunner


class TestDatabaseIsolationTests(SimpleTestCase):
    def test_runner_refuses_to_use_the_application_database(self):
        connection = SimpleNamespace(
            settings_dict={
                'NAME': '/tmp/greaterwms.sqlite3',
                'TEST': {'NAME': '/tmp/greaterwms.sqlite3'},
            },
            vendor='sqlite',
        )
        with patch('greaterwms.test_runner.connections') as connections_mock:
            connections_mock.__iter__.return_value = ['default']
            connections_mock.__getitem__.return_value = connection
            with self.assertRaises(ImproperlyConfigured):
                IsolatedDatabaseTestRunner(verbosity=0).setup_databases()


class DataValidationTests(TestCase):
    def test_data_validator_accepts_regular_text_and_rejects_script_or_select(self):
        self.assertEqual(data_validate('regular goods name'), 'regular goods name')
        for value in ('<script>alert(1)</script>', 'select * from goods'):
            with self.subTest(value=value), self.assertRaises(APIException):
                data_validate(value)

    def test_quantity_validators_enforce_their_ranges(self):
        self.assertEqual(qty_0_data_validate(1), 1)
        self.assertEqual(qty_data_validate(0), 0)
        with self.assertRaises(APIException):
            qty_0_data_validate(0)
        with self.assertRaises(APIException):
            qty_data_validate(-1)

    def test_document_code_validators_increment_numeric_suffix(self):
        self.assertEqual(dn_data_validate('DN00000001'), 'DN00000001')
        self.assertEqual(dn_data_validate('DN00000002'), 'DN00000003')
        self.assertEqual(asn_data_validate('ASN00000001'), 'ASN00000001')
        self.assertEqual(asn_data_validate('ASN00000002'), 'ASN00000003')

    def test_sum_number_and_transport_calculations(self):
        self.assertEqual(sumOfList([2, 3, 5], 3), 10)
        self.assertEqual(sumOfList([], 0), 0)
        self.assertTrue(is_number('12.5'))
        self.assertTrue(is_number('Ⅳ'))
        self.assertFalse(is_number('not a number'))
        self.assertEqual(transportation_calculate(10, 4, 2, 3, 5), 20)
        self.assertEqual(transportation_calculate(1, 1, 1, 1, 5), 5)

    def test_barcode_round_trip(self):
        payload = {'goods_code': 'TEST-001', 'qty': 3}
        self.assertEqual(verify_bar_code(secret_bar_code(payload)), payload)

    def test_openid_and_appid_validators_require_existing_user(self):
        user = Users.objects.create(
            name='Test User',
            openid='valid-openid',
            appid='valid-appid',
            t_code='transaction',
            ip='127.0.0.1',
        )
        self.assertEqual(openid_validate(user.openid), user.openid)
        self.assertEqual(appid_validate(user.appid), user.appid)
        with self.assertRaises(APIException):
            openid_validate('unknown-openid')
        with self.assertRaises(APIException):
            appid_validate('unknown-appid')


class BackendApiSmokeTests(AuthenticatedAPITestCase):
    def test_create_simple_master_data_records(self):
        requests = (
            ('/goodsunit/', {'goods_unit': 'API Unit', 'creater': 'Test Staff'}),
            ('/goodsclass/', {'goods_class': 'API Class', 'creater': 'Test Staff'}),
            ('/goodsbrand/', {'goods_brand': 'API Brand', 'creater': 'Test Staff'}),
            ('/goodscolor/', {'goods_color': 'API Color', 'creater': 'Test Staff'}),
            ('/goodsshape/', {'goods_shape': 'API Shape', 'creater': 'Test Staff'}),
            ('/goodsspecs/', {'goods_specs': 'API Specs', 'creater': 'Test Staff'}),
            ('/goodsorigin/', {'goods_origin': 'API Origin', 'creater': 'Test Staff'}),
            ('/binsize/', {
                'bin_size': 'API Bin Size',
                'bin_size_w': 1,
                'bin_size_d': 2,
                'bin_size_h': 3,
                'creater': 'Test Staff',
            }),
            ('/capital/', {
                'capital_name': 'API Capital',
                'capital_qty': 2,
                'capital_cost': 12.5,
                'creater': 'Test Staff',
            }),
            ('/payment/freight/', {
                'send_city': 'Origin',
                'receiver_city': 'Destination',
                'weight_fee': 1.5,
                'volume_fee': 2.5,
                'min_payment': 3,
                'transportation_supplier': 'Carrier',
                'creater': 'Test Staff',
            }),
        )
        for endpoint, payload in requests:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, payload, format='json')
                self.assertEqual(response.status_code, 200, getattr(response, 'data', None))

    def test_authenticated_list_endpoints_are_reachable(self):
        endpoints = (
            '/staff/',
            '/staff/type/',
            '/binset/',
            '/binsize/',
            '/binproperty/',
            '/capital/',
            '/driver/',
            '/stock/list/',
            '/stock/bin/',
            '/company/',
            '/cyclecount/',
            '/cyclecount/cyclecountrecorder/',
            '/cyclecount/qtyrecorviewset/',
            '/cyclecount/getgoodscyclecount/',
            '/dashboard/receipts/',
            '/dashboard/sales/',
            '/supplier/',
            '/supplier/file/',
            '/customer/',
            '/customer/file/',
            '/warehouse/',
            '/warehouse/multiple/',
            '/goods/',
            '/goods/file/',
            '/goodsunit/',
            '/goodsclass/',
            '/goodscolor/',
            '/goodsbrand/',
            '/goodsshape/',
            '/goodsspecs/',
            '/goodsorigin/',
            '/scanner/',
            '/asn/list/',
            '/asn/detail/',
            '/asn/filelist/',
            '/asn/filedetail/',
            '/dn/list/',
            '/dn/detail/',
            '/dn/pickinglistfilter/',
            '/dn/filelist/',
            '/dn/filedetail/',
            '/payment/freight/',
            '/payment/freightfile/',
            '/stock/filelist/',
            '/stock/filebinlist/',
            '/driver/dispatchlist/',
            '/driver/file/',
            '/capital/file/',
            '/binsize/file/',
            '/binset/file/',
            '/cyclecount/filecyclecountday/',
            '/cyclecount/filecyclecountall/',
            '/cyclecount/manualfilecyclecount/',
            '/staff/file/',
        )
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(response.status_code, 200, getattr(response, 'data', None))

    def test_protected_api_requires_a_valid_token(self):
        unauthenticated = APIClient().get('/company/')
        self.assertEqual(unauthenticated.status_code, 200)
        self.assertEqual(unauthenticated.data['status_code'], 500)

        invalid_token_client = APIClient()
        invalid_token_client.credentials(HTTP_TOKEN='not-a-user')
        invalid_token = invalid_token_client.get('/company/')
        self.assertEqual(invalid_token.status_code, 200)
        self.assertEqual(invalid_token.data['status_code'], 500)

    def test_root_redirects_to_backend_api_documentation(self):
        response = self.client.get('/', follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/api/docs/')
