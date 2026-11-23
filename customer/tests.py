from .models import ListModel as Customer
from utils.test_helpers import AuthenticatedAPITestCase


class CustomerWorkflowTests(AuthenticatedAPITestCase):
    def test_create_update_and_soft_delete_customer(self):
        response = self.client.post('/customer/', {
            'customer_name': 'API Customer',
            'customer_city': 'Town',
            'customer_address': '1 Main Street',
            'customer_contact': '555-0100',
            'customer_manager': 'Manager',
            'customer_level': 1,
            'creater': 'Test Staff',
        }, format='json')

        self.assertEqual(response.status_code, 200, getattr(response, 'data', None))
        customer = Customer.objects.get(openid=self.openid, customer_name='API Customer')

        response = self.client.patch(
            f'/customer/{customer.id}/',
            {'customer_city': 'Updated Town'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, getattr(response, 'data', None))
        customer.refresh_from_db()
        self.assertEqual(customer.customer_city, 'Updated Town')

        response = self.client.delete(f'/customer/{customer.id}/')
        self.assertEqual(response.status_code, 200, getattr(response, 'data', None))
        customer.refresh_from_db()
        self.assertTrue(customer.is_delete)