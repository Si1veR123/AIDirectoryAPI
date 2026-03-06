from tool.models import Tool
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Clear embeddings for all tools"

    def handle(self, *args, **kwargs):
        tools = Tool.objects.filter(embedding__isnull=False)
        count = tools.count()
        tools.update(embedding=None)
        self.stdout.write(f"Cleared embeddings for {count} tools.")