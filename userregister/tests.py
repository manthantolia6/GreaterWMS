import json
from unittest.mock import patch

from django.test import TestCase

from company.models import ListModel as Company
from staff.models import ListModel as Staff
from userprofile.models import Users
from warehouse.models import ListModel as Warehouse


class RegistrationWorkflowTests(TestCase):
    def test_mismatched_passwords_do_not_create_an_account(self):
        with patch('userregister.views.os.path.exists', return_value=True):
            response = self.client.post(
                '/register/',
                data=json.dumps({
                    'name': 'new-user',
                    'password1': 'first-password',
                    'password2': 'different-password',
                }),
                content_type='application/json',
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Users.objects.exists())

    def test_missing_password_does_not_create_an_account(self):
        with patch('userregister.views.os.path.exists', return_value=True):
            response = self.client.post(
                '/register/',
                data=json.dumps({'name': 'new-user'}),
                content_type='application/json',
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Users.objects.exists())

    def test_registration_creates_tenant_defaults_without_filesystem_side_effects(self):
        with patch('userregister.views.os.path.exists', return_value=True):
            response = self.client.post(
                '/register/',
                data=json.dumps({
                    'name': 'new-user',
                    'password1': 'strong-password',
                    'password2': 'strong-password',
                }),
                content_type='application/json',
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Users.objects.filter(name='new-user').exists())
        self.assertTrue(Staff.objects.filter(staff_name='new-user').exists())
        self.assertTrue(Company.objects.filter(company_name='GreaterWMS').exists())
        self.assertTrue(Warehouse.objects.filter(warehouse_name='Center Warehouse').exists())