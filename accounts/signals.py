from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    """Create a Profile once per user; never double-create on signup."""
    Profile.objects.get_or_create(user=instance)
