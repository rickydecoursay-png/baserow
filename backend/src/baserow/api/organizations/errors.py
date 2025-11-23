from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

ERROR_ORGANIZATION_DOES_NOT_EXIST = (
    "ERROR_ORGANIZATION_DOES_NOT_EXIST",
    HTTP_404_NOT_FOUND,
    "The organization does not exist.",
)

ERROR_ORGANIZATION_USER_DOES_NOT_EXIST = (
    "ERROR_ORGANIZATION_USER_DOES_NOT_EXIST",
    HTTP_404_NOT_FOUND,
    "The organization user does not exist.",
)

ERROR_ORGANIZATION_USER_ALREADY_EXISTS = (
    "ERROR_ORGANIZATION_USER_ALREADY_EXISTS",
    HTTP_400_BAD_REQUEST,
    "The user is already a member of the organization.",
)

ERROR_USER_NOT_IN_ORGANIZATION = (
    "ERROR_USER_NOT_IN_ORGANIZATION",
    HTTP_400_BAD_REQUEST,
    "The user is not a member of the organization.",
)

ERROR_LAST_ADMIN_OF_ORGANIZATION = (
    "ERROR_LAST_ADMIN_OF_ORGANIZATION",
    HTTP_400_BAD_REQUEST,
    "Cannot remove or demote the last admin of the organization.",
)

ERROR_CANNOT_DELETE_YOURSELF_FROM_ORGANIZATION = (
    "ERROR_CANNOT_DELETE_YOURSELF_FROM_ORGANIZATION",
    HTTP_400_BAD_REQUEST,
    "You cannot remove yourself from the organization.",
)
