from rest_framework import serializers
from .models import Tool, Developer, Domain, Accessibility, ContextWindow, RecommendationResults

class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ['name']

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['name']

class AccessibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessibility
        fields = ['name']

class ContextWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextWindow
        fields = ['name']

class ToolSerializer(serializers.ModelSerializer):
    developer = serializers.SlugRelatedField(queryset=Developer.objects.all(), slug_field='name')
    primary_domain = serializers.SlugRelatedField(queryset=Domain.objects.all(), slug_field='name')
    accessibility = serializers.SlugRelatedField(queryset=Accessibility.objects.all(), slug_field='name')
    context_window = serializers.SlugRelatedField(queryset=ContextWindow.objects.all(), slug_field='name')

    class Meta:
        model = Tool
        exclude = ['embedding']

class ToolNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['ai_name']

class RecommendationRequestSerializer(serializers.Serializer):
    q = serializers.CharField(required=True, help_text="The recommendation query prompt")
    top_n = serializers.IntegerField(required=False, default=5, min_value=1, max_value=100, help_text="Number of top recommendations to return (default=5, max=100)")

class RecommendationResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    results_id = serializers.IntegerField()
    results_url_http = serializers.CharField()
    results_url_ws = serializers.CharField()

class RecommendationResultsSerializer(serializers.ModelSerializer):
    recommended_tools = ToolSerializer(many=True)

    class Meta:
        model = RecommendationResults
        fields = '__all__'