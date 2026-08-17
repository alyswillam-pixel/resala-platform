from rest_framework import serializers

from resala_platform.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class LoginSerializer(serializers.Serializer):
    auc_email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
