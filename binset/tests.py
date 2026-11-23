from .models import ListModel as BinSet
from binsize.models import ListModel as BinSize
from binproperty.models import ListModel as BinProperty
from utils.test_helpers import AuthenticatedAPITestCase


class BinSetWorkflowTests(AuthenticatedAPITestCase):
    def test_bin_create_partial_update_and_barcode_lookup(self):
        BinSize.objects.create(
            bin_size='Medium',
            bin_size_w=1,
            bin_size_d=1,
            bin_size_h=1,
            creater='Test Staff',
            openid=self.openid,
        )
        BinProperty.objects.create(
            bin_property='Normal',
            creater='Test Staff',
            openid=self.openid,
        )
        created = self.client.post(
            '/binset/',
            {
                'bin_name': 'API Bin',
                'bin_size': 'Medium',
                'bin_property': 'Normal',
                'bar_code': 'api-bin-barcode',
                'creater': 'Test Staff',
            },
            format='json',
        )

        self.assertEqual(created.status_code, 200, created.data)
        binset = BinSet.objects.get(openid=self.openid, bin_name='API Bin')

        updated = self.client.patch(
            '/binset/{}/'.format(binset.id),
            {'bin_size': 'Medium', 'bin_property': 'Normal'},
            format='json',
        )
        self.assertEqual(updated.status_code, 200, updated.data)
        binset.refresh_from_db()
        self.assertEqual(binset.bin_property, 'Normal')

        tag = self.client.get('/binset/scannerbintag/{}/'.format(binset.bar_code))
        self.assertEqual(tag.status_code, 200, getattr(tag, 'data', None))
        self.assertEqual(tag.data['bin_name'], 'API Bin')