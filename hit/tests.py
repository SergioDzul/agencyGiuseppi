from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from profiles.models import CustomUser, Job
from hit.models import Hit


# Create your tests here.
class HitTestCase(TestCase):
    def setUp(self) -> None:
        self.big_boss = CustomUser.objects.create_superuser(email="sergio@test.com", username="bigboss",password="zxczxc.123")
        manager_job = Job.objects.create(name="Manager")
        hitman_job = Job.objects.create(name="Hitman", report_to=manager_job)
        user_base = {
            "gender": "M",
            "birthday": timezone.now(),
            "terms_and_conditions": True,
            "country": "MX",
            "state": "YUC",
        }
        user_base.update({
            "email": "mangager@test.com",
            "job": manager_job
        })
        self.manager = CustomUser.objects.create(**user_base)
        user_base.update({
            "email": "hitman@test.com",
            "job": hitman_job,
            "report_to": self.manager
        })
        self.hitman = CustomUser.objects.create(**user_base)
        self.hit_data_base = {
            "target_name": "Sergio",
            "description": "Test",
            "created_by": self.manager
        }

    def test_create(self) -> None:
        Hit.objects.create(**self.hit_data_base)
        self.assertEqual(Hit.objects.count(), 1, "the creation hit doesn't work")

    def test_assigment_happy_path(self) -> None:
        hit = Hit.objects.create(**self.hit_data_base)
        hit.assigned_to = self.hitman
        try:
            hit.save()
        except ValidationError:
            self.fail("Save in happy path, this isn't supposed to be broken")

    def test_assignment_method(self) -> None:
        hit = Hit.objects.create(**self.hit_data_base)
        hit.assign(self.hitman)
        hit.refresh_from_db()
        self.assertEqual(hit.assigned_to.pk, self.hitman.pk, "It's not the same id")
        self.assertEqual(hit.status, 2, "It's not the number, the assignment value")

    def test_we_can_not_assign_a_hit_to_big_boss(self) -> None:
        local_data = self.hit_data_base.copy()
        local_data.update({
            "assigned_to": self.big_boss,
            "created_by": self.big_boss
        })

        def tmp(*args, **kwargs):
            Hit.objects.create(**local_data)

        self.assertRaises(ValidationError, tmp, "Its suppose raise an validation error")

    def test_we_can_not_assign_a_hit_to_inactive_user(self) -> None:
        hit = Hit.objects.create(**self.hit_data_base)
        # logic delete, see the Custom user tests
        self.hitman.delete()
        hit.assigned_to = self.hitman
        self.assertRaises(ValidationError, hit.save, "Its suppose to raise a ValidationError for inactive user")

    def test_a_hit_with_final_status_can_not_be_changed(self) -> None:
        hit = Hit.objects.create(**self.hit_data_base)
        hit.assign(self.hitman)
        hit.refresh_from_db()
        # COMPLETED = 4
        hit.status = 4
        hit.save()
        hit.refresh_from_db()
        hit.status = 2
        self.assertRaises(ValidationError, hit.save, "Its suppose to raise a ValidationError for final state")
