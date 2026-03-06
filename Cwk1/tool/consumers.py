import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import RecommendationResults
from .serializers import RecommendationResultsSerializer

class RecommendationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        # 1. Authentication check
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.results_id = self.scope["url_route"]["kwargs"]["results_id"]

        # 2. Fetch results
        result = await self.get_results()

        if result is None:
            await self.accept()
            await self.send_json({"type": "recommendation_error", "detail": "Results not found"})
            await self.close()
            return

        # 3. Ownership check
        if result.user_id != user.id and not user.is_staff:
            await self.accept()
            await self.send_json({"type": "recommendation_error", "detail": "You can only view your own recommendations"})
            await self.close()
            return

        # 4. Accept socket
        await self.accept()

        # 5. If results already exist, send them immediately
        if await self.results_ready(result):
            data = await self.serialize(result)
            await self.send_json(data)

            await self.close()
            return

        # 6. Otherwise subscribe for completion event
        self.group_name = f"recommend_{self.results_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def recommendation_ready(self, message):
        await self.send_json(message)
        await self.close()
    
    @sync_to_async
    def get_results(self):
        try:
            return RecommendationResults.objects.get(pk=self.results_id)
        except RecommendationResults.DoesNotExist:
            return None


    @sync_to_async
    def results_ready(self, result):
        return result.recommended_tools.exists()


    @sync_to_async
    def serialize(self, result):
        return {
            "type": "recommendation_ready",
            "detail": RecommendationResultsSerializer(result).data,
        }