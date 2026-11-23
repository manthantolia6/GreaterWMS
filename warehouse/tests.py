from .models import ListModel as Warehouse
from utils.test_helpers import AuthenticatedAPITestCase


class WarehouseWorkflowTests(AuthenticatedAPITestCase):
    def payload(self, name='API Warehouse'):
        return {
            'warehouse_name': name,
            'warehouse_city': 'Town',
            'warehouse_address': '1 Main Street',
            'warehouse_contact': '5550100',
            'warehouse_manager': 'Manager',
            'creater': 'Test Staff',
        }

    def test_warehouse_limit_update_and_soft_delete(self):
        response = self.client.post('/warehouse/', self.payload(), format='json')

        self.assertEqual(response.status_code, 200, response.data)
        warehouse = Warehouse.objects.get(openid=self.openid, warehouse_name='API Warehouse')

        second = self.client.post('/warehouse/', self.payload('Second Warehouse'), format='json')
        self.assertGreaterEqual(second.data['status_code'], 400)
        self.assertEqual(Warehouse.objects.filter(openid=self.openid, is_delete=False).count(), 1)

        updated = self.client.patch(
            '/warehouse/{}/'.format(warehouse.id),
            {'warehouse_name': 'Updated Warehouse'},
            format='json',
        )
        self.assertEqual(updated.status_code, 200, updated.data)
        warehouse.refresh_from_db()
        self.assertEqual(warehouse.warehouse_name, 'Updated Warehouse')

        deleted = self.client.delete('/warehouse/{}/'.format(warehouse.id))
        self.assertEqual(deleted.status_code, 200, deleted.data)
        warehouse.refresh_from_db()
        self.assertTrue(warehouse.is_delete)