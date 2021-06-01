from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import (AbstractUser, UserManager)
from django.core.exceptions import ValidationError
from django.utils import timezone
from profiles.utils import create_hash

GENDER_OPTIONS = (
    ('M', _('Male')),
    ('F', _('Female'))
)


class Job(models.Model):
    """
    Generic tree of jobs, if the organization grows, we can diagram it here
    """
    name = models.CharField(
        max_length=150,
        verbose_name=_("Job title name"),
        null=False
    )
    report_to = models.ForeignKey(
        "self",
        related_name="team",
        blank=True,
        null=True,
        on_delete=models.SET_NULL)

    def __unicode__(self) -> str:  # pragma: no cover
        return self.name

    def __str__(self) -> str:
        return self.__unicode__()

    def validate_chain_of_command(self, job) -> None:
        """
        Check parameter job, instance of Job class
        validate the Chain of Command.
        :param Job job: Job instance
        :raise ValidationError: the job parameter is not a son of the job
        :return:
        """
        if self.report_to.pk != job.pk:
            raise ValidationError("It's an Enterprise organization Error")


class CustomUser(AbstractUser):
    """
    custom user model
    """
    email = models.EmailField(
        _('Email address'),
        unique=True
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        editable=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        default=create_hash,
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    hash = models.CharField(
        max_length=150,
        default=create_hash,
        editable=False
    )
    gender = models.CharField(
        max_length=1,
        verbose_name=_("Gender"),
        choices=GENDER_OPTIONS,
        null=True
    )
    birthday = models.DateField(
        null=True,
        verbose_name=_("Birthday")
    )
    terms_and_conditions = models.BooleanField(
        default=False,
        verbose_name=_("Accept terms and conditions")
    )
    country = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_("Country")
    )
    state = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_("State")
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created at"),
        editable=False,
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated at"),
        editable=False,
        auto_now=True
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('This field is used to define if the user still active in the organization'),
    )
    deleted_at = models.DateTimeField(
        verbose_name=_("Deleted at"),
        null=True
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True)
    report_to = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = [
            ("can_change_to_inactivate", _("Can deactivate users")),
            ("can_edit_hitman", _("Can edit hitman data"))
        ]
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['hash']),
            models.Index(fields=['email']),
            models.Index(fields=['gender']),
            models.Index(fields=['country', 'state']),
            models.Index(fields=['created_at'])
        ]

    def __unicode__(self) -> str:  # pragma: no cover
        username = self.username
        full_name = "%s %s" % (self.first_name, self.last_name)
        if not username:
            # Anonymous user
            return "Anon"
        if len(full_name) > 3:
            return full_name
        return username

    def __str__(self) -> str:
        return self.__unicode__()

    def get_full_name(self) -> str:
        full_name = "%s %s" % (self.first_name, self.last_name)
        out_name = full_name.strip()
        if out_name == "":
            return self.username
        return out_name

    def delete(self, using=None, keep_parents=False) -> None:
        self.is_active = False
        self.deleted_at = timezone.now()
        return self.save()

    def save(self, *args, **kwargs) -> None:
        with transaction.atomic():
            if not self.is_superuser:
                if self.report_to:
                    self.job.validate_chain_of_command(self.report_to.job)
                return super(CustomUser, self).save(*args, **kwargs)
            elif CustomUser.objects.exclude(id=self.pk).filter(is_superuser=True).exists():
                raise ValidationError("Only exist one Big Boss")
            return super(CustomUser, self).save(*args, **kwargs)
