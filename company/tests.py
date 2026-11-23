from userprofile.models import Users

from utils.test_helpers import AuthenticatedAPITestCase


class CompanyApiTests(AuthenticatedAPITestCase):
    endpoint = '/company/'

    def company_payload(self, name='Test Company'):
        return {
            'company_name': name,
            'company_city': 'Test City',
            'company_address': '1 Test Street',
            'company_contact': '123456789',
            'company_manager': 'Test Manager',
            'creater': 'Test Staff',
        }

    def test_company_create_update_soft_delete_and_list(self):
        create = self.client.post(self.endpoint, self.company_payload(), format='json')
        self.assertEqual(create.status_code, 200, create.data)
        company_id = create.data['id']

        update = self.client.patch(
            '{}{}/'.format(self.endpoint, company_id),
            {'company_city': 'Updated City'},
            format='json',
        )
        self.assertEqual(update.status_code, 200, update.data)
        self.assertEqual(update.data['company_city'], 'Updated City')

        listing = self.client.get(self.endpoint)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual([item['id'] for item in listing.data['results']], [company_id])

        deleted = self.client.delete('{}{}/'.format(self.endpoint, company_id))
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(self.client.get(self.endpoint).data['results'], [])

    def test_company_isolation_and_single_company_rule(self):
        other_user = Users.objects.create(
            name='Other User',
            openid='other-openid',
            appid='other-appid',
            t_code='other-transaction',
            ip='127.0.0.1',
        )
        create = self.client.post(self.endpoint, self.company_payload(), format='json')
        self.assertEqual(create.status_code, 200, create.data)

        duplicate = self.client.post(
            self.endpoint,
            self.company_payload(name='Another Company'),
            format='json',
        )
        self.assertGreaterEqual(duplicate.data['status_code'], 400)

        self.client.credentials(HTTP_TOKEN=other_user.openid)
        self.assertEqual(self.client.get(self.endpoint).data['results'], [])