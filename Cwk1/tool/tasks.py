from django.core.mail import send_mail
from user.models import CustomUser
from django.tasks import task
from django.conf import settings
from .models import Tool, RecommendationResults
from . import embedding_index
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import RecommendationResultsSerializer
from django.utils import timezone

@task
def send_domain_email(tool_name, domain, url):
    users = CustomUser.objects.filter(interested_domain__name=domain, email_alerts=True)
    emails = [user.email for user in users if user.email]

    send_mail(
        subject="New tool in your interested domain",
        message=f"{tool_name} is a new tool in your interested domain {domain}. Check it out at {url}!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails
    )

BATCH_SIZE = 16

@task
def compute_tool_embeddings(tool_ids: list[int], update_recommender: bool = True, verbose: bool = False):
    # Fetch all tools in one query
    tools = list(Tool.objects.filter(pk__in=tool_ids))

    for batch_start in range(0, len(tools), BATCH_SIZE):
        batch_tools = tools[batch_start:batch_start + BATCH_SIZE]

        texts = [f"{tool.ai_name} {tool.key_functionality}" for tool in batch_tools]
        embeddings = embedding_index.get_model().encode(texts, convert_to_numpy=True)

        for tool, embedding in zip(batch_tools, embeddings):
            tool.embedding = embedding.tolist()

        # Bulk update this batch
        Tool.objects.bulk_update(batch_tools, ["embedding"])

        # Update recommender for each tool in this batch
        if update_recommender:
            for tool, embedding in zip(batch_tools, embeddings):
                embedding_index.get_recommender().update_embedding(tool.pk, embedding)
        
        if verbose:
            print(f"Processed batch {batch_start // BATCH_SIZE + 1} of {(len(tools) - 1) // BATCH_SIZE + 1}")

@task
def create_recommendation(results_id: int, query: str, top_n: int = 5):
    result = RecommendationResults.objects.get(pk=results_id)

    recommended_tools = embedding_index.get_recommender().recommend(query, top_n=top_n)
    if recommended_tools is None:
        message = {
            "type": "recommendation_error",
            "detail": "Error computing recommendations."
        }
        result.completed_at = timezone.now()
        result.error = "No tools with embeddings available for recommendation."
        result.save()
    else:
        result.recommended_tools.set(recommended_tools)
        result.completed_at = timezone.now()
        result.save()

        serializer = RecommendationResultsSerializer(result)
        message = {
            "type": "recommendation_ready",
            "detail": serializer.data
        }

    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            f"recommend_{results_id}",
            message
        )