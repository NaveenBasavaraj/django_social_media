from rest_framework import serializers
from django.conf import settings

from core.abstract.serializers import AbstractSerializers
from core.user.models import User


class UserSerializer(AbstractSerializers):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation["avatar"]:
            representation["avatar"] = settings.DEFAULT_AVATAR_URL
            return representation
        if settings.DEBUG:  # debug enabled for dev
            request = self.context.get("request")
            representation["avatar"] = request.build_absolute_uri(
                representation["avatar"]
            )
        return representation

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "avatar",
            "is_active",
            "created",
            "updated",
        ]
        read_only_field = ["is_active"]
