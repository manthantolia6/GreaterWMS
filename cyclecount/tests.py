from django.utils import timezone

from cyclecount.models import CyclecountModeDayModel, ManualCyclecountModeModel
from stock.models import StockBinModel

from utils.test_helpers import AuthenticatedAPITestCase


class CycleCountWorkflowTests(AuthenticatedAPITestCase):
    def test_submitted_count_records_physical_quantity_and_variance(self):
        count = CyclecountModeDayModel.objects.create(
            openid=self.openid,
            cyclecount_status=0,
            bin_name='A010101',
            goods_code='TEST-001',
            goods_qty=10,
            physical_inventory=0,
            difference=0,
            creater='Test Staff',
            t_code='count-transaction',
        )

        response = self.client.post(
            '/cyclecount/',
            [{
                't_code': count.t_code,
                'goods_qty': 10,
                'physical_inventory': 8,
            }],
            format='json',
        )

        self.assertEqual(response.status_code, 200, response.data)
        count.refresh_from_db()
        self.assertEqual(count.physical_inventory, 8)
        self.assertEqual(count.difference, -2)
        self.assertEqual(count.cyclecount_status, 1)

    def test_cycle_count_list_is_scoped_to_the_current_tenant(self):
        own_count = CyclecountModeDayModel.objects.create(
            openid=self.openid,
            cyclecount_status=1,
            bin_name='A010101',
            goods_code='OWN-GOODS',
            goods_qty=2,
            physical_inventory=2,
            difference=0,
            creater='Test Staff',
            t_code='own-count',
        )
        CyclecountModeDayModel.objects.create(
            openid='other-openid',
            cyclecount_status=1,
            bin_name='B010101',
            goods_code='OTHER-GOODS',
            goods_qty=9,
            physical_inventory=9,
            difference=0,
            creater='Other',
            t_code='other-count',
        )

        response = self.client.get('/cyclecount/cyclecountrecorder/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row['id'] for row in response.data['results']], [own_count.id])

    def test_manual_cycle_count_scans_bins_and_records_variance(self):
        StockBinModel.objects.create(
            bin_name='Manual Count Bin',
            goods_code='TEST-001',
            goods_desc='Test product',
            goods_qty=10,
            bin_size='Medium',
            bin_property='Normal',
            t_code='manual-count-bin',
            openid=self.openid,
            create_time=timezone.now(),
        )

        scan = self.client.get('/cyclecount/getgoodscyclecount/', {'goods_code': 'TEST-001'})

        self.assertEqual(scan.status_code, 200, getattr(scan, 'data', None))
        count = ManualCyclecountModeModel.objects.get(
            openid=self.openid,
            bin_name='Manual Count Bin',
            goods_code='TEST-001',
            cyclecount_status=0,
        )
        submit = self.client.post(
            '/cyclecount/manualcyclecount/',
            [{
                't_code': count.t_code,
                'goods_qty': count.goods_qty,
                'physical_inventory': 8,
            }],
            format='json',
        )

        self.assertEqual(submit.status_code, 200, submit.data)
        count.refresh_from_db()
        self.assertEqual(count.physical_inventory, 8)
        self.assertEqual(count.difference, -2)
        self.assertEqual(count.cyclecount_status, 1)