from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Tool
from .tasks import send_domain_email, compute_tool_embeddings
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

@receiver(post_save, sender=Tool)
def update_tool_embedding(sender, instance, created, **kwargs):
    if created:
        if instance.pk:
            compute_tool_embeddings.enqueue(tool_ids=[instance.pk])
        return

    update_fields = kwargs.get("update_fields")

    # If update_fields is specified, only trigger if relevant fields are included
    if update_fields is not None:
        if not ({"ai_name", "key_functionality"} & set(update_fields)):
            return

    # Otherwise, compare with the stored version to detect changes
    else:
        try:
            old = Tool.objects.get(pk=instance.pk)
        except Tool.DoesNotExist:
            return

        if old.ai_name == instance.ai_name and old.key_functionality == instance.key_functionality:
            return

    compute_tool_embeddings.enqueue(tool_ids=[instance.pk])