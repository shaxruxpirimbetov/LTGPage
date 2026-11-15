from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Registration: only these fields are accepted, the password is never returned."""

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UpdateUserSerializer(serializers.ModelSerializer):
    """Profile update: no permission flags (is_staff, is_superuser, ...) can be changed here."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])
        return instance


class AdminUpdateUserSerializer(UpdateUserSerializer):
    """Used for superusers only: additionally allows (de)activating an account."""

    class Meta(UpdateUserSerializer.Meta):
        fields = UpdateUserSerializer.Meta.fields + ["is_active"]


class ResponseUserSerializer(serializers.ModelSerializer):
    """Public representation: shown to everyone, so no e-mail."""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]