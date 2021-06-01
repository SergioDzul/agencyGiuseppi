from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# use numbers for performance reasons in queries
UNASSIGNED = 1
ASSIGNED = 2
FAILED = 3
COMPLETED = 4

STATES = (
    (UNASSIGNED, _("Unassigned")),
    (ASSIGNED, _("Assigned")),
    (FAILED, _("Failed")),
    (COMPLETED, _("Completed"))
)


# Create your models here.
class Hit(models.Model):
    assigned_to = models.ForeignKey(
        "profiles.CustomUser",
        related_name="hits",
        verbose_name=_("Assigned to"),
        null=True,
        on_delete=models.CASCADE,
    )
    target_name = models.CharField(verbose_name=_("Target name"), max_length=150)
    description = models.CharField(verbose_name=_("Description"), max_length=250)
    status = models.PositiveSmallIntegerField(
        choices=STATES,
        default=UNASSIGNED,
        verbose_name=_("Status")
    )
    created_by = models.ForeignKey(
        "profiles.CustomUser",
        verbose_name=_("Created by"),
        on_delete=models.SET_NULL,
        null=True
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

    class Meta:
        verbose_name = _("hit")
        verbose_name_plural = _("hits")
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at']),
        ]


    def assign(self, user) -> None:
        # Check if is an user instance without the isinstance to prevent the importation
        if not hasattr(user, 'is_active'):
            raise ValidationError("user parameter must be an User instance")
        self.assigned_to = user
        self.status = ASSIGNED
        return self.save()

    def save(self, *args, **kwargs) -> None:
        with transaction.atomic():
            if self.assigned_to and self.assigned_to.is_superuser:
                raise ValidationError("You can assign a hit to Big boss")
            if self.assigned_to and not self.assigned_to.is_active:
                raise ValidationError("You can't assign a hit to an inactive user")
            if self.id:
                current = Hit.objects.get(id=self.id)
                if current.status in [FAILED, COMPLETED]:
                    raise ValidationError("A Hit in a end status can't be changed")
            return super(Hit, self).save(*args, **kwargs)
