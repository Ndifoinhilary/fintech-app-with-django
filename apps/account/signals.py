from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.account.models import Profile


User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a user profile when a new user is created.
    :param sender: The model class.
    :param instance: The instance of the model.
    :param created: Boolean indicating if the instance was created.
    :param kwargs: Additional keyword arguments.
    """
    if created:
        Profile.objects.create(user=instance)



@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the user profile when the user is saved.
    :param sender: The model class.
    :param instance: The instance of the model.
    :param kwargs: Additional keyword arguments.
    """
    instance.profile.save()