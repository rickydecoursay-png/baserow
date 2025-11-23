from django.urls import re_path

from .views import (
    OrganizationUsersView,
    OrganizationUserView,
    OrganizationsView,
    OrganizationView,
)

app_name = "baserow.api.organizations"

urlpatterns = [
    re_path(r"^$", OrganizationsView.as_view(), name="list"),
    re_path(
        r"^(?P<organization_id>[0-9]+)/$",
        OrganizationView.as_view(),
        name="item",
    ),
    re_path(
        r"^(?P<organization_id>[0-9]+)/users/$",
        OrganizationUsersView.as_view(),
        name="users",
    ),
    re_path(
        r"^(?P<organization_id>[0-9]+)/users/(?P<organization_user_id>[0-9]+)/$",
        OrganizationUserView.as_view(),
        name="user",
    ),
]
