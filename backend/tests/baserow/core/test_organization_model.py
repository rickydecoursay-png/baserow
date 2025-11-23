"""
Tests for Organization model and OrganizationHandler.
"""
from datetime import datetime, timezone

import pytest
from freezegun import freeze_time

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
from baserow.core.organization_handler import OrganizationHandler


@pytest.mark.django_db
def test_create_organization(data_fixture):
    """Test creating an organization."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user, name="Test Organization")
    
    assert organization.name == "Test Organization"
    assert organization.id is not None
    assert not organization.trashed
    
    # Verify the creator is automatically added as an admin
    org_user = OrganizationUser.objects.get(
        organization=organization, user=user
    )
    assert org_user.permissions == ORGANIZATION_USER_PERMISSION_ADMIN


@pytest.mark.django_db
def test_get_organization(data_fixture):
    """Test retrieving an organization."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    created_org = handler.create_organization(user=user, name="Test Org")
    retrieved_org = handler.get_organization(created_org.id)
    
    assert retrieved_org.id == created_org.id
    assert retrieved_org.name == "Test Org"


@pytest.mark.django_db
def test_get_organization_does_not_exist(data_fixture):
    """Test getting a non-existent organization raises an exception."""
    handler = OrganizationHandler()
    
    with pytest.raises(OrganizationDoesNotExist):
        handler.get_organization(999999)


@pytest.mark.django_db
def test_update_organization(data_fixture):
    """Test updating an organization."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user, name="Old Name")
    updated_org = handler.update_organization(
        organization=organization,
        name="New Name"
    )
    
    assert updated_org.name == "New Name"


@pytest.mark.django_db
def test_delete_organization(data_fixture):
    """Test deleting an organization."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user, name="Test Org")
    org_id = organization.id
    
    handler.delete_organization(organization)
    
    assert not Organization.objects.filter(id=org_id).exists()


@pytest.mark.django_db
def test_add_user_to_organization(data_fixture):
    """Test adding a user to an organization."""
    user1 = data_fixture.create_user()
    user2 = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user1, name="Test Org")
    org_user = handler.add_user_to_organization(
        organization=organization,
        user=user2,
        permissions=ORGANIZATION_USER_PERMISSION_MEMBER
    )
    
    assert org_user.user == user2
    assert org_user.organization == organization
    assert org_user.permissions == ORGANIZATION_USER_PERMISSION_MEMBER


@pytest.mark.django_db
def test_add_user_already_exists(data_fixture):
    """Test adding a user that already exists raises an exception."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user, name="Test Org")
    
    # Try to add the same user again
    with pytest.raises(OrganizationUserAlreadyExists):
        handler.add_user_to_organization(
            organization=organization,
            user=user,
            permissions=ORGANIZATION_USER_PERMISSION_MEMBER
        )


@pytest.mark.django_db
def test_remove_user_from_organization(data_fixture):
    """Test removing a user from an organization."""
    user1 = data_fixture.create_user()
    user2 = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user1, name="Test Org")
    handler.add_user_to_organization(
        organization=organization,
        user=user2,
        permissions=ORGANIZATION_USER_PERMISSION_MEMBER
    )
    
    handler.remove_user_from_organization(
        organization=organization,
        user=user2,
        removed_by=user1
    )
    
    assert not OrganizationUser.objects.filter(
        organization=organization, user=user2, trashed=False
    ).exists()


@pytest.mark.django_db
def test_cannot_remove_yourself(data_fixture):
    """Test that a user cannot remove themselves."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user, name="Test Org")
    
    with pytest.raises(CannotDeleteYourselfFromOrganization):
        handler.remove_user_from_organization(
            organization=organization,
            user=user,
            removed_by=user
        )


@pytest.mark.django_db
def test_cannot_remove_last_admin(data_fixture):
    """Test that the last admin cannot be removed."""
    user1 = data_fixture.create_user()
    user2 = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user1, name="Test Org")
    handler.add_user_to_organization(
        organization=organization,
        user=user2,
        permissions=ORGANIZATION_USER_PERMISSION_MEMBER
    )
    
    # Try to remove the only admin
    with pytest.raises(LastAdminOfOrganization):
        handler.remove_user_from_organization(
            organization=organization,
            user=user1,
            removed_by=user2
        )


@pytest.mark.django_db
def test_update_organization_user_permissions(data_fixture):
    """Test updating organization user permissions."""
    user1 = data_fixture.create_user()
    user2 = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user1, name="Test Org")
    org_user = handler.add_user_to_organization(
        organization=organization,
        user=user2,
        permissions=ORGANIZATION_USER_PERMISSION_MEMBER
    )
    
    updated_org_user = handler.update_organization_user(
        organization_user=org_user,
        permissions=ORGANIZATION_USER_PERMISSION_ADMIN
    )
    
    assert updated_org_user.permissions == ORGANIZATION_USER_PERMISSION_ADMIN


@pytest.mark.django_db
def test_cannot_demote_last_admin(data_fixture):
    """Test that the last admin cannot be demoted."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    organization = handler.create_organization(user=user, name="Test Org")
    org_user = OrganizationUser.objects.get(
        organization=organization, user=user
    )
    
    with pytest.raises(LastAdminOfOrganization):
        handler.update_organization_user(
            organization_user=org_user,
            permissions=ORGANIZATION_USER_PERMISSION_MEMBER
        )


@pytest.mark.django_db
def test_organization_created_and_updated_on(data_fixture):
    """Test that created_on and updated_on timestamps work correctly."""
    user = data_fixture.create_user()
    handler = OrganizationHandler()
    
    with freeze_time("2020-01-01 12:00"):
        organization = handler.create_organization(user=user, name="Test Org")
    
    assert organization.created_on == datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert organization.updated_on == datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
    
    with freeze_time("2020-01-02 12:00"):
        organization.name = "Updated Org"
        organization.save()
    
    assert organization.created_on == datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert organization.updated_on == datetime(2020, 1, 2, 12, 0, tzinfo=timezone.utc)


@pytest.mark.django_db
def test_organization_user_get_last_order(data_fixture):
    """Test getting the last order for organization users."""
    user = data_fixture.create_user()
    
    assert OrganizationUser.get_last_order(user) == 1
    
    handler = OrganizationHandler()
    org1 = handler.create_organization(user=user, name="Org 1")
    
    # After creating one organization, the user should have order 0
    # Next order should be 1
    assert OrganizationUser.get_last_order(user) == 1
