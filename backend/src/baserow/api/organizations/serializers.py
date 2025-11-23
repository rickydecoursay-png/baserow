from rest_framework import serializers

from baserow.core.models import Organization, OrganizationUser

__all__ = [
    "OrganizationSerializer",
    "OrganizationUserSerializer",
]


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "created_on",
            "updated_on",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "created_on": {"read_only": True},
            "updated_on": {"read_only": True},
        }


class OrganizationUserSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationUser model."""

    class Meta:
        model = OrganizationUser
        fields = (
            "id",
            "organization",
            "user",
            "permissions",
            "created_on",
            "updated_on",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "created_on": {"read_only": True},
            "updated_on": {"read_only": True},
        }
