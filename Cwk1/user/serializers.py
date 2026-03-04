from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = get_user_model()
        fields = "__all__"

    def validate(self, attrs):
        # If updating, use existing instance values
        if self.instance:
            username = attrs.get("username", self.instance.username)
            email = attrs.get("email", self.instance.email)
        else:
            username = attrs.get("username")
            email = attrs.get("email")

        password = attrs.get("password")
        if password:
            temp_user = CustomUser(
                username=username,
                email=email,
            )
            validate_password(password, temp_user)

        return attrs

    def create(self, data):
        user = get_user_model().objects.create_user(**data)
        return user

    def update(self, instance, data):
        password = data.pop("password", None)
        if password:
            instance.set_password(password)
            
        # Update all other fields normally
        for attr, value in data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance