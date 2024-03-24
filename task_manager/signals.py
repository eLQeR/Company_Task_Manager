from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_password(sender, instance, created, **kwargs):
    instance.set_password(instance.password)
