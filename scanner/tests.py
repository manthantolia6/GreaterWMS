from scanner.models import ListModel as Scanner

from utils.test_helpers import AuthenticatedAPITestCase


class ScannerWorkflowTests(AuthenticatedAPITestCase):
    def test_process_qr_code_can_be_created_and_decoded(self):
        created = self.client.post('/scanner/', {'process': 'stock-count'}, format='json')
        self.assertEqual(created.status_code, 200, created.data)

        scanner = Scanner.objects.get(openid=self.openid, bar_code=created.data['bar_code'])
        retrieved = self.client.get('/scanner/list/{}/'.format(scanner.bar_code))
        decoded = self.client.post('/scanner/query/', {'code': scanner.code}, format='json')

        self.assertEqual(retrieved.status_code, 200, retrieved.data)
        self.assertEqual(retrieved.data['mode'], 'stock-count')
        self.assertEqual(decoded.status_code, 200, decoded.data)
        self.assertTrue(decoded.data['status'])
        self.assertEqual(decoded.data['data']['data']['process'], 'stock-count')

    def test_scanner_create_requires_a_process_name(self):
        response = self.client.post('/scanner/', {}, format='json')
        self.assertEqual(response.data['status_code'], 500)
        self.assertFalse(Scanner.objects.filter(openid=self.openid).exists())