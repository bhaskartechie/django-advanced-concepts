from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, UserLog


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, bio=f"Bio for {instance.username}")
        UserLog.objects.create(
            user=instance, action=f"User {instance.username} created"
        )


@receiver(post_save, sender=User)
def log_email_update(sender, instance, **kwargs):
    if not instance._state.adding:  # Check if it's an update, not creation
        # Access previous state using get_deferred_fields or custom logic
        try:
            old_instance = User.objects.get(id=instance.id)
            if old_instance.email != instance.email:
                UserLog.objects.create(
                    user=instance, action=f"Email updated to {instance.email}"
                )
        except User.DoesNotExist:
            pass
