from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Tool
from .tasks import send_domain_email
from django.conf import settings

@receiver(pre_save, sender=Tool)
def detect_domain_change(sender, instance, **kwargs):
    if settings.DEFAULT_FROM_EMAIL is None:
        print("Email credentials not configured. Skipping email notifications.")
        return

    if instance.pk:
        old = Tool.objects.get(pk=instance.pk)
        if old.primary_domain == instance.primary_domain:
            return

    send_domain_email.enqueue(
        tool_name=str(instance.ai_name),
        domain=str(instance.primary_domain),
        url=str(instance.website_url)
    )