from django.test import TestCase
from django.core.exceptions import ValidationError
from profiles.models import CustomUser, Job
from profiles.utils import create_hash
from django.utils import timezone


# Create your tests here.
class ProfileTest(TestCase):

    def test_creation(self) -> None:
        print("[Profiles] Test job creations")
        try:
            Job.objects.bulk_create([
                Job(**item) for item in [{"name": "Manager"}, {"name": "Hitman"}]
            ])
        except Exception as e:
            self.fail("bulk_create() raised ExceptionType unexpectedly!")
        self.assertEqual(Job.objects.count(), 2, "It must be two profiles")

    def test_report_to(self) -> None:
        general_manager = Job.objects.create(name="General Manager")
        try:
            test = Job.objects.create(name="IT Manager", report_to=general_manager)
        except Exception as e:
            self.fail("report to can be assignment")
        self.assertNotEqual(test.pk, 0, "assignment error in profile")
        self.assertEqual(test.report_to.pk, general_manager.pk, "wrong assignment")

    def test_create_organization_tree(self) -> None:
        """
                                                General-manager
                  IT-manager                       seller-manager                      Product-manager
        front-end back-end UX-engineer    tele-marketing social-manager

        :return:
        """
        general_manager = Job.objects.create(name="General Manager")
        it_manager = Job.objects.create(name="IT Manager", report_to=general_manager)
        seller_manager = Job.objects.create(name="Seller Manager", report_to=general_manager)
        front_end_dev = Job.objects.create(name="Front-end Developer", report_to=it_manager)

        self.assertEqual(front_end_dev.report_to.pk, it_manager.pk, "slayer assignment doesn't work")
        self.assertEqual(
            front_end_dev.report_to.report_to.pk,
            general_manager.pk,
            "slayer assignment doesn't work")

        try:
            front_end_dev.validate_chain_of_command(it_manager)
        except ValidationError:
            self.fail("It shouldn't raise a ValidationError")

        def tmp(*args, **kwargs):
            front_end_dev.validate_chain_of_command(seller_manager)
        self.assertRaises(ValidationError, tmp, "It's supposed to raise a ValidationError but it doesn't")


class CustomUSerTestCase(TestCase):

    def test_create_superuser_command(self) -> None:
        print("[Profiles] super user command must be work as usual")
        CustomUser.objects.create_superuser(
            username=create_hash(),
            email="sergio@test.com",
            password="pass"
        )
        self.assertEqual(CustomUser.objects.count(), 1, "It must be only one user")

    def test_only_one_big_boss(self) -> None:
        print("[Profiles] only one superuser")
        CustomUser.objects.create_superuser(
            username=create_hash(),
            email="sergio1@test.com",
            password="pass"
        )

        def tmp(*args, **kwargs):
            CustomUser.objects.create_superuser(
                username=create_hash(),
                email="sergio2@test.com",
                password="pass"
            )
        self.assertRaises(
            ValidationError,
            tmp,
            "It should be raise an exception trying to create another superuser"
        )
        self.assertEqual(CustomUser.objects.count(), 1, "It must be only one user")

    def test_inherent_the_boss_title(self) -> None:
        """
        What about the boss's retirement? then wee gone a need a new one.
        """
        old_boss = CustomUser.objects.create_superuser(
            username=create_hash(),
            email="sergio1@test.com",
            password="pass"
        )
        old_boss.is_superuser=False
        old_boss.save()

        CustomUser.objects.create_superuser(
            username=create_hash(),
            email="sergio2@test.com",
            password="pass"
        )
        self.assertEqual(CustomUser.objects.count(), 2, "It's suppose to have the old and the new big boss")

    def test_create_user(self) -> None:
        CustomUser.objects.create_superuser(email="sergio@test.com", username="bigboss", password="pass")
        manager_job = Job.objects.create(**{"name": "Manager"})
        try:
            CustomUser.objects.create(**{
                "email": "mangager@test.com",
                "gender": "F",
                "birthday": timezone.now(),
                "terms_and_conditions": True,
                "country": "MX",
                "state": "YUC",
                "job": manager_job,
            })
        except Exception:
            self.fail("Error in create user")

    def test_organization(self) -> None:
        CustomUser.objects.create_superuser(email="sergio@test.com", username="bigboss", password="pass")
        manager_job = Job.objects.create(**{"name": "Manager"})
        manager2_job = Job.objects.create(**{"name": "Manager"})
        hitman_job = Job.objects.create(**{"name": "Hitman", "report_to": manager_job})
        manager_base = {
            "gender": "F",
            "birthday": timezone.now(),
            "terms_and_conditions": True,
            "country": "MX",
            "state": "YUC",
        }
        manager_base.update({
            "email": "mangager@test.com",
            "job": manager_job
        })

        manager1 = CustomUser.objects.create(**manager_base)
        manager_base.update({
            "email": "mangager2@test.com",
            "job": manager2_job,
        })
        manager2 = CustomUser.objects.create(**manager_base)
        base_hitman = {
            "email": "hitman@test.com",
            "gender": "F",
            "birthday": timezone.now(),
            "terms_and_conditions": True,
            "country": "MX",
            "state": "YUC",
            "job": hitman_job
        }
        try:
            base_hitman.update({"report_to": manager1})
            CustomUser.objects.create(**base_hitman)
        except Exception:
            self.fail("Fail in happy path in chain of command")

        def tmp(*args, **kwargs):
            base_hitman.update({"report_to": manager2, "email": "hitman2@test.com"})
            CustomUser.objects.create(**base_hitman)
        self.assertRaises(ValidationError, tmp, "it's suppose to raise a ValidationError")

    def test_logic_deletion(self) -> None:
        manager_job = Job.objects.create(**{"name": "Manager"})

        tmp = CustomUser.objects.create(**{
            "email": "managager3@test.com",
            "gender": "F",
            "birthday": timezone.now(),
            "terms_and_conditions": True,
            "country": "MX",
            "state": "YUC",
            "job": manager_job,
        })
        tmp.delete()
        self.assertEqual(CustomUser.objects.count(), 1, "It's suppose to do an update, not a delete action")
        from_db = CustomUser.objects.get(email="managager3@test.com")
        self.assertFalse(from_db.is_active, "it's suppose to be False")
        self.assertIsNotNone(from_db.deleted_at, "it's suppose to not to be None")
