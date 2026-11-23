import json

from django.contrib.auth.models import User
from django.test import TestCase

from staff.models import ListModel as Staff
from userprofile.models import Users


class LoginWorkflowTests(TestCase):
    def test_unknown_username_returns_login_error(self):
        response = self.client.post(
            '/login/',
            data=json.dumps({'name': 'missing-user', 'password': 'password'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())
        self.assertFalse(User.objects.exists())

    def test_valid_credentials_resolve_staff_and_openid(self):
        user = User.objects.create_user(username='alice', password='strong-password')
        openid = 'login-openid'
        Users.objects.create(
            user_id=user.id,
            name='Alice',
            openid=openid,
            appid='login-appid',
            t_code='login-transaction',
            ip='127.0.0.1',
        )
        staff = Staff.objects.create(staff_name='Alice', staff_type='Admin', openid=openid)

        response = self.client.post(
            '/login/',
            data=json.dumps({'name': 'alice', 'password': 'strong-password'}),
            content_type='application/json',
            HTTP_X_FORWARDED_FOR='192.0.2.10',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['openid'], openid)
        self.assertEqual(response.json()['data']['user_id'], staff.id)
        self.assertEqual(response.json()['ip'], '192.0.2.10')

    def test_wrong_password_does_not_authenticate(self):
        User.objects.create_user(username='alice', password='strong-password')

        response = self.client.post(
            '/login/',
            data=json.dumps({'name': 'alice', 'password': 'wrong-password'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('openid', response.json().get('data', {}))