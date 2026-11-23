from .models import ListModel as Supplier
from utils.test_helpers import AuthenticatedAPITestCase


class SupplierWorkflowTests(AuthenticatedAPITestCase):
    def test_create_update_and_soft_delete_supplier(self):
        response = self.client.post('/supplier/', {
            'supplier_name': 'API Supplier',
            'supplier_city': 'Town',
            'supplier_address': '2 Main Street',
            'supplier_contact': '555-0200',
            'supplier_manager': 'Manager',
            'supplier_level': 1,
            'creater': 'Test Staff',
        }, format='json')

        self.assertEqual(response.status_code, 200, getattr(response, 'data', None))
        supplier = Supplier.objects.get(openid=self.openid, supplier_name='API Supplier')

        response = self.client.patch(
            f'/supplier/{supplier.id}/',
            {'supplier_city': 'Updated Town'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, getattr(response, 'data', None))
        supplier.refresh_from_db()
        self.assertEqual(supplier.supplier_city, 'Updated Town')

        response = self.client.delete(f'/supplier/{supplier.id}/')
        self.assertEqual(response.status_code, 200, getattr(response, 'data', None))
        supplier.refresh_from_db()
        self.assertTrue(supplier.is_delete)