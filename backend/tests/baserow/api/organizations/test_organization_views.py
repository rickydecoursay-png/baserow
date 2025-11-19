"""
Tests for Organization API endpoints.
"""
from django.shortcuts import reverse

import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from baserow.core.models import Organization, OrganizationUser


@pytest.mark.django_db
def test_list_organizations(api_client, data_fixture):
    """Test listing organizations for a user."""
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password"
    )
    
    # Create a few organizations
    org1 = Organization.objects.create(name="Org 1")
    org2 = Organization.objects.create(name="Org 2")
    org3 = Organization.objects.create(name="Org 3")
    
    # Add user to org1 and org2
    OrganizationUser.objects.create(
        organization=org1, user=user, order=0, permissions="ADMIN"
    )
    OrganizationUser.objects.create(
        organization=org2, user=user, order=1, permissions="MEMBER"
    )
    
    response = api_client.get(
        reverse("api:organizations:list"),
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json[0]["name"] == "Org 1"
    assert response_json[1]["name"] == "Org 2"


@pytest.mark.django_db
def test_create_organization(api_client, data_fixture):
    """Test creating a new organization."""
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password"
    )
    
    response = api_client.post(
        reverse("api:organizations:list"),
        {"name": "New Organization"},
        format="json",
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_201_CREATED
    response_json = response.json()
    assert response_json["name"] == "New Organization"
    assert "id" in response_json
    
    # Verify the organization was created
    org = Organization.objects.get(id=response_json["id"])
    assert org.name == "New Organization"
    
    # Verify the creator is an admin
    org_user = OrganizationUser.objects.get(organization=org, user=user)
    assert org_user.permissions == "ADMIN"


@pytest.mark.django_db
def test_get_organization(api_client, data_fixture):
    """Test retrieving a specific organization."""
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password"
    )
    
    org = Organization.objects.create(name="Test Org")
    OrganizationUser.objects.create(
        organization=org, user=user, order=0, permissions="ADMIN"
    )
    
    response = api_client.get(
        reverse("api:organizations:item", kwargs={"organization_id": org.id}),
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert response_json["id"] == org.id
    assert response_json["name"] == "Test Org"


@pytest.mark.django_db
def test_get_organization_not_found(api_client, data_fixture):
    """Test retrieving a non-existent organization."""
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password"
    )
    
    response = api_client.get(
        reverse("api:organizations:item", kwargs={"organization_id": 999999}),
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_organization(api_client, data_fixture):
    """Test updating an organization."""
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password"
    )
    
    org = Organization.objects.create(name="Old Name")
    OrganizationUser.objects.create(
        organization=org, user=user, order=0, permissions="ADMIN"
    )
    
    response = api_client.patch(
        reverse("api:organizations:item", kwargs={"organization_id": org.id}),
        {"name": "New Name"},
        format="json",
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert response_json["name"] == "New Name"
    
    # Verify the database was updated
    org.refresh_from_db()
    assert org.name == "New Name"


@pytest.mark.django_db
def test_delete_organization(api_client, data_fixture):
    """Test deleting an organization."""
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password"
    )
    
    org = Organization.objects.create(name="Test Org")
    OrganizationUser.objects.create(
        organization=org, user=user, order=0, permissions="ADMIN"
    )
    
    response = api_client.delete(
        reverse("api:organizations:item", kwargs={"organization_id": org.id}),
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_204_NO_CONTENT
    
    # Verify the organization was deleted
    assert not Organization.objects.filter(id=org.id).exists()


@pytest.mark.django_db
def test_list_organization_users(api_client, data_fixture):
    """Test listing users in an organization."""
    user1, token = data_fixture.create_user_and_token(
        email="user1@test.nl", password="password"
    )
    user2 = data_fixture.create_user(email="user2@test.nl")
    
    org = Organization.objects.create(name="Test Org")
    org_user1 = OrganizationUser.objects.create(
        organization=org, user=user1, order=0, permissions="ADMIN"
    )
    org_user2 = OrganizationUser.objects.create(
        organization=org, user=user2, order=1, permissions="MEMBER"
    )
    
    response = api_client.get(
        reverse("api:organizations:users", kwargs={"organization_id": org.id}),
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json[0]["id"] == org_user1.id
    assert response_json[0]["permissions"] == "ADMIN"
    assert response_json[1]["id"] == org_user2.id
    assert response_json[1]["permissions"] == "MEMBER"


@pytest.mark.django_db
def test_update_organization_user(api_client, data_fixture):
    """Test updating organization user permissions."""
    user1, token = data_fixture.create_user_and_token(
        email="user1@test.nl", password="password"
    )
    user2 = data_fixture.create_user(email="user2@test.nl")
    
    org = Organization.objects.create(name="Test Org")
    OrganizationUser.objects.create(
        organization=org, user=user1, order=0, permissions="ADMIN"
    )
    org_user2 = OrganizationUser.objects.create(
        organization=org, user=user2, order=1, permissions="MEMBER"
    )
    
    response = api_client.patch(
        reverse(
            "api:organizations:user",
            kwargs={
                "organization_id": org.id,
                "organization_user_id": org_user2.id
            }
        ),
        {"permissions": "ADMIN"},
        format="json",
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert response_json["permissions"] == "ADMIN"
    
    # Verify the database was updated
    org_user2.refresh_from_db()
    assert org_user2.permissions == "ADMIN"


@pytest.mark.django_db
def test_delete_organization_user(api_client, data_fixture):
    """Test removing a user from an organization."""
    user1, token = data_fixture.create_user_and_token(
        email="user1@test.nl", password="password"
    )
    user2 = data_fixture.create_user(email="user2@test.nl")
    
    org = Organization.objects.create(name="Test Org")
    OrganizationUser.objects.create(
        organization=org, user=user1, order=0, permissions="ADMIN"
    )
    org_user2 = OrganizationUser.objects.create(
        organization=org, user=user2, order=1, permissions="MEMBER"
    )
    
    response = api_client.delete(
        reverse(
            "api:organizations:user",
            kwargs={
                "organization_id": org.id,
                "organization_user_id": org_user2.id
            }
        ),
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_204_NO_CONTENT
    
    # Verify the user was removed
    assert not OrganizationUser.objects.filter(id=org_user2.id).exists()


@pytest.mark.django_db
def test_cannot_remove_last_admin(api_client, data_fixture):
    """Test that the last admin cannot be removed."""
    user1, token = data_fixture.create_user_and_token(
        email="user1@test.nl", password="password"
    )
    user2 = data_fixture.create_user(email="user2@test.nl")
    
    org = Organization.objects.create(name="Test Org")
    org_user1 = OrganizationUser.objects.create(
        organization=org, user=user1, order=0, permissions="ADMIN"
    )
    OrganizationUser.objects.create(
        organization=org, user=user2, order=1, permissions="MEMBER"
    )
    
    # Try to remove the only admin (as user2 trying to remove user1 would fail
    # with cannot delete yourself, but the handler would catch last admin)
    # Let's test demoting instead
    response = api_client.patch(
        reverse(
            "api:organizations:user",
            kwargs={
                "organization_id": org.id,
                "organization_user_id": org_user1.id
            }
        ),
        {"permissions": "MEMBER"},
        format="json",
        **{"HTTP_AUTHORIZATION": f"JWT {token}"}
    )
    
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "ERROR_LAST_ADMIN_OF_ORGANIZATION" in str(response.content)
