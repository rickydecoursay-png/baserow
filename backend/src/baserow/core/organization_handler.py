"""
Organization handler for managing Organization CRUD operations.
"""
from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import transaction

from baserow.core.exceptions import (
    CannotDeleteYourselfFromOrganization,
    LastAdminOfOrganization,
    OrganizationDoesNotExist,
    OrganizationUserAlreadyExists,
    OrganizationUserDoesNotExist,
    UserNotInOrganization,
)
from baserow.core.models import (
    ORGANIZATION_USER_PERMISSION_ADMIN,
    ORGANIZATION_USER_PERMISSION_MEMBER,
    Organization,
    OrganizationUser,
)


class OrganizationHandler:
    """
    Handler for managing organizations and organization memberships.
    """

    def create_organization(
        self, user: AbstractUser, name: str
    ) -> Organization:
        """
        Creates a new organization for the specified user.

        :param user: The user creating the organization.
        :param name: The name of the organization.
        :return: The newly created organization.
        """
        with transaction.atomic():
            organization = Organization.objects.create(name=name)
            
            # Automatically add the creator as an admin
            self.add_user_to_organization(
                organization=organization,
                user=user,
                permissions=ORGANIZATION_USER_PERMISSION_ADMIN,
            )
            
        return organization

    def get_organization(self, organization_id: int) -> Organization:
        """
        Gets an organization by ID.

        :param organization_id: The ID of the organization.
        :return: The organization instance.
        :raises OrganizationDoesNotExist: If the organization doesn't exist.
        """
        try:
            return Organization.objects.get(id=organization_id, trashed=False)
        except Organization.DoesNotExist:
            raise OrganizationDoesNotExist(
                f"Organization with ID {organization_id} does not exist."
            )

    def update_organization(
        self,
        organization: Organization,
        name: Optional[str] = None,
    ) -> Organization:
        """
        Updates an organization.

        :param organization: The organization to update.
        :param name: Optional new name for the organization.
        :return: The updated organization.
        """
        if name is not None:
            organization.name = name
            organization.save(update_fields=["name", "updated_on"])
        
        return organization

    def delete_organization(self, organization: Organization) -> None:
        """
        Deletes an organization.

        :param organization: The organization to delete.
        """
        organization.delete()

    def add_user_to_organization(
        self,
        organization: Organization,
        user: AbstractUser,
        permissions: str = ORGANIZATION_USER_PERMISSION_MEMBER,
    ) -> OrganizationUser:
        """
        Adds a user to an organization.

        :param organization: The organization to add the user to.
        :param user: The user to add.
        :param permissions: The permissions to grant (ADMIN or MEMBER).
        :return: The created OrganizationUser instance.
        :raises OrganizationUserAlreadyExists: If the user is already in the organization.
        """
        if OrganizationUser.objects.filter(
            organization=organization, user=user, trashed=False
        ).exists():
            raise OrganizationUserAlreadyExists(
                f"User {user.id} is already a member of organization {organization.id}."
            )

        order = OrganizationUser.get_last_order(user)
        organization_user = OrganizationUser.objects.create(
            organization=organization,
            user=user,
            order=order,
            permissions=permissions,
        )
        
        return organization_user

    def remove_user_from_organization(
        self,
        organization: Organization,
        user: AbstractUser,
        removed_by: AbstractUser,
    ) -> None:
        """
        Removes a user from an organization.

        :param organization: The organization to remove the user from.
        :param user: The user to remove.
        :param removed_by: The user performing the removal.
        :raises UserNotInOrganization: If the user is not in the organization.
        :raises CannotDeleteYourselfFromOrganization: If trying to remove yourself.
        :raises LastAdminOfOrganization: If removing the last admin.
        """
        if user == removed_by:
            raise CannotDeleteYourselfFromOrganization(
                "You cannot remove yourself from an organization."
            )

        try:
            organization_user = OrganizationUser.objects.get(
                organization=organization, user=user, trashed=False
            )
        except OrganizationUser.DoesNotExist:
            raise UserNotInOrganization(
                f"User {user.id} is not a member of organization {organization.id}."
            )

        # Check if this is the last admin
        if organization_user.permissions == ORGANIZATION_USER_PERMISSION_ADMIN:
            admin_count = OrganizationUser.objects.filter(
                organization=organization,
                permissions=ORGANIZATION_USER_PERMISSION_ADMIN,
                trashed=False,
            ).count()
            
            if admin_count <= 1:
                raise LastAdminOfOrganization(
                    "Cannot remove the last admin from the organization."
                )

        organization_user.delete()

    def get_organization_user(
        self, organization: Organization, user: AbstractUser
    ) -> OrganizationUser:
        """
        Gets the OrganizationUser instance for a user in an organization.

        :param organization: The organization.
        :param user: The user.
        :return: The OrganizationUser instance.
        :raises OrganizationUserDoesNotExist: If the user is not in the organization.
        """
        try:
            return OrganizationUser.objects.get(
                organization=organization, user=user, trashed=False
            )
        except OrganizationUser.DoesNotExist:
            raise OrganizationUserDoesNotExist(
                f"User {user.id} is not a member of organization {organization.id}."
            )

    def update_organization_user(
        self,
        organization_user: OrganizationUser,
        permissions: Optional[str] = None,
    ) -> OrganizationUser:
        """
        Updates an organization user's permissions.

        :param organization_user: The organization user to update.
        :param permissions: Optional new permissions (ADMIN or MEMBER).
        :return: The updated organization user.
        :raises LastAdminOfOrganization: If demoting the last admin.
        """
        if permissions is not None:
            # Prevent demoting the last admin
            if (
                organization_user.permissions == ORGANIZATION_USER_PERMISSION_ADMIN
                and permissions != ORGANIZATION_USER_PERMISSION_ADMIN
            ):
                admin_count = OrganizationUser.objects.filter(
                    organization=organization_user.organization,
                    permissions=ORGANIZATION_USER_PERMISSION_ADMIN,
                    trashed=False,
                ).count()
                
                if admin_count <= 1:
                    raise LastAdminOfOrganization(
                        "Cannot demote the last admin of the organization."
                    )
            
            organization_user.permissions = permissions
            organization_user.save(update_fields=["permissions", "updated_on"])
        
        return organization_user
