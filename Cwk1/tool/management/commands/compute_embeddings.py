from tool.tasks import compute_tool_embeddings
from tool.models import Tool
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Compute embeddings for all tools"

    def handle(self, *args, **kwargs):
        tool_ids = list(Tool.objects.values_list('id', flat=True))
        compute_tool_embeddings.enqueue(tool_ids, update_recommender=False, verbose=True)
        self.stdout.write("Enqueued embedding computation task for all tools.")