from .models import ListModel as Driver
from utils.test_helpers import AuthenticatedAPITestCase


class DriverWorkflowTests(AuthenticatedAPITestCase):
    def test_driver_crud_is_tenant_scoped(self):
        created = self.client.post(
            '/driver/',
            {
                'driver_name': 'API Driver',
                'license_plate': 'API-123',
                'contact': '5550100',
                'creater': 'Test Staff',
            },
            format='json',
        )

        self.assertEqual(created.status_code, 200, created.data)
        driver = Driver.objects.get(openid=self.openid, driver_name='API Driver')

        updated = self.client.patch(
            '/driver/{}/'.format(driver.id),
            {'license_plate': 'API-456'},
            format='json',
        )
        self.assertEqual(updated.status_code, 200, updated.data)
        driver.refresh_from_db()
        self.assertEqual(driver.license_plate, 'API-456')

        deleted = self.client.delete('/driver/{}/'.format(driver.id))
        self.assertEqual(deleted.status_code, 200, deleted.data)
        driver.refresh_from_db()
        self.assertTrue(driver.is_delete)