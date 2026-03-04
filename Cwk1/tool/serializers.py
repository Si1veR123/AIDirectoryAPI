from rest_framework import serializers
from .models import Tool, Developer, Domain, Accessibility, ContextWindow

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
        fields = '__all__'
