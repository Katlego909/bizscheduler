from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, VendorProfile

@receiver(post_save, sender=User)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created and instance.is_vendor:
        # Profile created in form.save(), so only needed if extra logic required
        VendorProfile.objects.get_or_create(user=instance)
