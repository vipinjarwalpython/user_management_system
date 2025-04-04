from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.
    Includes password validation and write-only password field.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
            "is_active",
            "failed_tasks",
        )
        read_only_fields = ("failed_tasks",)
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def create(self, validated_data):
        """
        Override the default create method to use the custom create_user method
        which handles password hashing.
        """
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user's basic information (excluding email and password).
    Admin or manager can use this for profile updates.
    """
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "is_active")
        read_only_fields = ("email",)
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user status (active/inactive) and failed task count.
    Likely used by an admin or system logic to mark user status.
    """
    class Meta:
        model = User
        fields = ("id", "is_active", "failed_tasks")
        read_only_fields = ("id",)
