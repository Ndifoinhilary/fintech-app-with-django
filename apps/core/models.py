import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

User = get_user_model()


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContentView(TimeStampedModel):
    """
    Model to track content views.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_('Content Type'))
    object_id = models.UUIDField(verbose_name=_('Object ID'))
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('User'))
    ip_address = models.GenericIPAddressField(verbose_name=_('IP Address'), blank=True, null=True)
    last_viewed = models.DateTimeField()

    class Meta:
        verbose_name = _('Content View')
        verbose_name_plural = _('Content Views')
        ordering = ['-last_viewed']
        unique_together = ('content_type', 'object_id', 'user', 'ip_address')

    def __str__(self):
        return (
            f"{self.content_type} viewed by {self.user.get_full_name if self.user else 'Anonymous'} from IP {self.ip_address} "
        )

    @classmethod
    def record_view(cls, content_object, user=None, ip_address=None):
        """
        Record a view for a content object.
        :param content_object: The content object being viewed.
        :param user: The user viewing the content (optional).
        :param ip_address: The IP address of the viewer (optional).
        """
        content_type = ContentType.objects.get_for_model(content_object)
        try:
            view, create = cls.objects.get_or_create(
                content_type=content_type,
                object_id=content_object.id,
                user=user,
                ip_address=ip_address,
                defaults={'last_viewed': timezone.now()}
            )
            if not create:
                view.last_viewed = timezone.now()
                view.save(update_fields=['last_viewed'])

        except IntegrityError:
            pass