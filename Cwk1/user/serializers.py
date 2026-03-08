from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class SecureUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = get_user_model()
        fields = "__all__"

    USER_FIELDS = {
        "username", "first_name", "last_name", "password", "email",
        "email_alerts", "interested_domain", "date_of_birth",
        "bio", "favourite_tools"
    }

    SUPERUSER_FIELDS = set(f.name for f in CustomUser._meta.fields)

    STAFF_FIELDS = SUPERUSER_FIELDS - {
        "is_superuser", "groups", "user_permissions", "is_staff"
    }

    def validate(self, attrs):
        request_user = self.context["request"].user
        is_create = self.instance is None

        # Determine allowed fields based on requester
        if request_user.is_superuser:
            allowed_fields = self.SUPERUSER_FIELDS

        elif request_user.is_staff:
            allowed_fields = self.STAFF_FIELDS

        else:
            allowed_fields = self.USER_FIELDS

            # Normal users can only modify themselves
            if not is_create and self.instance != request_user:
                raise serializers.ValidationError(
                    "You can only modify your own account.",
                    code="permission_denied"
                )

        # Check field permissions
        for field in attrs.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(
                    f"You do not have permission to modify '{field}'.",
                    code="permission_denied"
                )

        # Handle username/email for password validation
        if self.instance:
            username = attrs.get("username", self.instance.username)
            email = attrs.get("email", self.instance.email)
        else:
            username = attrs.get("username")
            email = attrs.get("email")

        # Validate password if provided
        password = attrs.get("password")
        if password:
            temp_user = CustomUser(username=username, email=email)
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

class StandardUserSerializer(SecureUserSerializer):
    class Meta:
        model = get_user_model()
        fields = list(SecureUserSerializer.USER_FIELDS)