from .models import ListModel as Staff
from utils.test_helpers import AuthenticatedAPITestCase


class StaffVerificationWorkflowTests(AuthenticatedAPITestCase):
    def test_staff_is_locked_after_three_incorrect_codes(self):
        target = Staff.objects.create(
            staff_name='Verification Target',
            staff_type='Picker',
            check_code=1234,
            openid=self.openid,
        )

        for _ in range(3):
            self.client.get('/staff/', {
                'staff_name': target.staff_name,
                'check_code': 9999,
            })

        target.refresh_from_db()
        self.assertEqual(target.error_check_code_counter, 3)
        self.assertFalse(target.is_lock)

        response = self.client.get('/staff/', {
            'staff_name': target.staff_name,
            'check_code': 1234,
        })

        target.refresh_from_db()
        self.assertTrue(target.is_lock)
        self.assertEqual(target.error_check_code_counter, 0)
        self.assertIn('status_code', response.data)