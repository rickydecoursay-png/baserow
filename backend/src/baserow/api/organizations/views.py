from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from baserow.api.decorators import map_exceptions, validate_body
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.schemas import get_error_schema
from baserow.core.exceptions import (
    CannotDeleteYourselfFromOrganization,
    LastAdminOfOrganization,
    OrganizationDoesNotExist,
    OrganizationUserAlreadyExists,
    OrganizationUserDoesNotExist,
    UserNotInOrganization,
)
from baserow.core.models import Organization, OrganizationUser
from baserow.core.organization_handler import OrganizationHandler

from .errors import (
    ERROR_CANNOT_DELETE_YOURSELF_FROM_ORGANIZATION,
    ERROR_LAST_ADMIN_OF_ORGANIZATION,
    ERROR_ORGANIZATION_DOES_NOT_EXIST,
    ERROR_ORGANIZATION_USER_ALREADY_EXISTS,
    ERROR_ORGANIZATION_USER_DOES_NOT_EXIST,
    ERROR_USER_NOT_IN_ORGANIZATION,
)
from .serializers import OrganizationSerializer, OrganizationUserSerializer


class OrganizationsView(APIView):
    """API view for listing and creating organizations."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Organizations"],
        operation_id="list_organizations",
        description="Lists all organizations the authenticated user belongs to.",
        responses={
            200: OrganizationSerializer(many=True),
        },
    )
    def get(self, request):
        """List all organizations for the current user."""
        organizations = Organization.objects.filter(
            users=request.user, trashed=False
        ).distinct()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Organizations"],
        operation_id="create_organization",
        description="Creates a new organization for the authenticated user.",
        request=OrganizationSerializer,
        responses={
            201: OrganizationSerializer,
            400: get_error_schema(["ERROR_REQUEST_BODY_VALIDATION"]),
        },
    )
    @transaction.atomic
    @validate_body(OrganizationSerializer)
    def post(self, request, data):
        """Create a new organization."""
        handler = OrganizationHandler()
        organization = handler.create_organization(
            user=request.user,
            name=data.get("name"),
        )
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrganizationView(APIView):
    """API view for retrieving, updating, and deleting a specific organization."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            extend_schema.OpenApiParameter(
                name="organization_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization.",
            )
        ],
        tags=["Organizations"],
        operation_id="get_organization",
        description="Retrieves a specific organization by ID.",
        responses={
            200: OrganizationSerializer,
            404: get_error_schema([ERROR_ORGANIZATION_DOES_NOT_EXIST]),
        },
    )
    @map_exceptions(
        {
            OrganizationDoesNotExist: ERROR_ORGANIZATION_DOES_NOT_EXIST,
        }
    )
    def get(self, request, organization_id):
        """Get a specific organization."""
        handler = OrganizationHandler()
        organization = handler.get_organization(organization_id)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            extend_schema.OpenApiParameter(
                name="organization_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization.",
            )
        ],
        tags=["Organizations"],
        operation_id="update_organization",
        description="Updates a specific organization.",
        request=OrganizationSerializer,
        responses={
            200: OrganizationSerializer,
            400: get_error_schema(["ERROR_REQUEST_BODY_VALIDATION"]),
            404: get_error_schema([ERROR_ORGANIZATION_DOES_NOT_EXIST]),
        },
    )
    @transaction.atomic
    @validate_body(OrganizationSerializer, partial=True)
    @map_exceptions(
        {
            OrganizationDoesNotExist: ERROR_ORGANIZATION_DOES_NOT_EXIST,
        }
    )
    def patch(self, request, data, organization_id):
        """Update a specific organization."""
        handler = OrganizationHandler()
        organization = handler.get_organization(organization_id)
        organization = handler.update_organization(
            organization=organization,
            name=data.get("name"),
        )
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            extend_schema.OpenApiParameter(
                name="organization_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization.",
            )
        ],
        tags=["Organizations"],
        operation_id="delete_organization",
        description="Deletes a specific organization.",
        responses={
            204: None,
            404: get_error_schema([ERROR_ORGANIZATION_DOES_NOT_EXIST]),
        },
    )
    @transaction.atomic
    @map_exceptions(
        {
            OrganizationDoesNotExist: ERROR_ORGANIZATION_DOES_NOT_EXIST,
        }
    )
    def delete(self, request, organization_id):
        """Delete a specific organization."""
        handler = OrganizationHandler()
        organization = handler.get_organization(organization_id)
        handler.delete_organization(organization)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationUsersView(APIView):
    """API view for managing organization users."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            extend_schema.OpenApiParameter(
                name="organization_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization.",
            )
        ],
        tags=["Organizations"],
        operation_id="list_organization_users",
        description="Lists all users in a specific organization.",
        responses={
            200: OrganizationUserSerializer(many=True),
            404: get_error_schema([ERROR_ORGANIZATION_DOES_NOT_EXIST]),
        },
    )
    @map_exceptions(
        {
            OrganizationDoesNotExist: ERROR_ORGANIZATION_DOES_NOT_EXIST,
        }
    )
    def get(self, request, organization_id):
        """List all users in an organization."""
        handler = OrganizationHandler()
        organization = handler.get_organization(organization_id)
        organization_users = OrganizationUser.objects.filter(
            organization=organization, trashed=False
        )
        serializer = OrganizationUserSerializer(organization_users, many=True)
        return Response(serializer.data)


class OrganizationUserView(APIView):
    """API view for managing a specific organization user."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            extend_schema.OpenApiParameter(
                name="organization_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization.",
            ),
            extend_schema.OpenApiParameter(
                name="organization_user_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization user.",
            ),
        ],
        tags=["Organizations"],
        operation_id="update_organization_user",
        description="Updates a specific organization user's permissions.",
        request=OrganizationUserSerializer,
        responses={
            200: OrganizationUserSerializer,
            400: get_error_schema(["ERROR_REQUEST_BODY_VALIDATION"]),
            404: get_error_schema(
                [
                    ERROR_ORGANIZATION_DOES_NOT_EXIST,
                    ERROR_ORGANIZATION_USER_DOES_NOT_EXIST,
                ]
            ),
        },
    )
    @transaction.atomic
    @validate_body(OrganizationUserSerializer, partial=True)
    @map_exceptions(
        {
            OrganizationDoesNotExist: ERROR_ORGANIZATION_DOES_NOT_EXIST,
            OrganizationUserDoesNotExist: ERROR_ORGANIZATION_USER_DOES_NOT_EXIST,
            LastAdminOfOrganization: ERROR_LAST_ADMIN_OF_ORGANIZATION,
        }
    )
    def patch(self, request, data, organization_id, organization_user_id):
        """Update organization user permissions."""
        handler = OrganizationHandler()
        organization_user = OrganizationUser.objects.get(
            id=organization_user_id, organization_id=organization_id, trashed=False
        )
        organization_user = handler.update_organization_user(
            organization_user=organization_user,
            permissions=data.get("permissions"),
        )
        serializer = OrganizationUserSerializer(organization_user)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            extend_schema.OpenApiParameter(
                name="organization_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization.",
            ),
            extend_schema.OpenApiParameter(
                name="organization_user_id",
                location=extend_schema.OpenApiParameter.PATH,
                type=int,
                description="The ID of the organization user.",
            ),
        ],
        tags=["Organizations"],
        operation_id="delete_organization_user",
        description="Removes a user from an organization.",
        responses={
            204: None,
            400: get_error_schema(
                [
                    ERROR_CANNOT_DELETE_YOURSELF_FROM_ORGANIZATION,
                    ERROR_LAST_ADMIN_OF_ORGANIZATION,
                ]
            ),
            404: get_error_schema(
                [
                    ERROR_ORGANIZATION_DOES_NOT_EXIST,
                    ERROR_ORGANIZATION_USER_DOES_NOT_EXIST,
                ]
            ),
        },
    )
    @transaction.atomic
    @map_exceptions(
        {
            OrganizationDoesNotExist: ERROR_ORGANIZATION_DOES_NOT_EXIST,
            OrganizationUserDoesNotExist: ERROR_ORGANIZATION_USER_DOES_NOT_EXIST,
            UserNotInOrganization: ERROR_USER_NOT_IN_ORGANIZATION,
            CannotDeleteYourselfFromOrganization: ERROR_CANNOT_DELETE_YOURSELF_FROM_ORGANIZATION,
            LastAdminOfOrganization: ERROR_LAST_ADMIN_OF_ORGANIZATION,
        }
    )
    def delete(self, request, organization_id, organization_user_id):
        """Remove a user from an organization."""
        handler = OrganizationHandler()
        organization = handler.get_organization(organization_id)
        organization_user = OrganizationUser.objects.get(
            id=organization_user_id, organization_id=organization_id, trashed=False
        )
        handler.remove_user_from_organization(
            organization=organization,
            user=organization_user.user,
            removed_by=request.user,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
