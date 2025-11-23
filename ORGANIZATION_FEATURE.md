# Organization Feature

## Overview

This implementation adds a basic Organization structure to Baserow that serves as a hierarchical container for managing entities. Organizations provide a foundation for multi-tenant management and can be extended to contain multiple workspaces.

## Architecture

### Models

#### Organization
- **Purpose**: Top-level container for organizing users and resources
- **Fields**:
  - `name`: CharField - The name of the organization
  - `users`: ManyToManyField through OrganizationUser
  - `trashed`: BooleanField - Soft delete support
  - `created_on`, `updated_on`: DateTimeField - Audit timestamps

#### OrganizationUser
- **Purpose**: Represents a user's membership in an organization
- **Fields**:
  - `user`: ForeignKey to User
  - `organization`: ForeignKey to Organization
  - `order`: PositiveIntegerField - Display order
  - `permissions`: CharField - ADMIN or MEMBER
  - `trashed`: BooleanField - Soft delete support
  - `created_on`, `updated_on`: DateTimeField - Audit timestamps

### Permissions

- **ADMIN**: Can manage organization settings, add/remove users, and manage permissions
- **MEMBER**: Basic organization membership

### Business Rules

1. When creating an organization, the creator is automatically added as an ADMIN
2. The last ADMIN of an organization cannot be removed or demoted
3. Users cannot remove themselves from an organization (prevents accidental lockout)
4. Organizations support soft delete through the `trashed` flag

## API Endpoints

### Organizations

- `GET /api/organizations/` - List all organizations for the authenticated user
- `POST /api/organizations/` - Create a new organization
- `GET /api/organizations/{id}/` - Retrieve a specific organization
- `PATCH /api/organizations/{id}/` - Update an organization
- `DELETE /api/organizations/{id}/` - Delete an organization

### Organization Users

- `GET /api/organizations/{id}/users/` - List all users in an organization
- `PATCH /api/organizations/{id}/users/{user_id}/` - Update user permissions
- `DELETE /api/organizations/{id}/users/{user_id}/` - Remove a user from an organization

## Usage Examples

### Creating an Organization

```python
from baserow.core.organization_handler import OrganizationHandler

handler = OrganizationHandler()
organization = handler.create_organization(
    user=request.user,
    name="My Organization"
)
```

### Adding a User to an Organization

```python
handler.add_user_to_organization(
    organization=organization,
    user=new_user,
    permissions=ORGANIZATION_USER_PERMISSION_MEMBER
)
```

### Updating Organization User Permissions

```python
handler.update_organization_user(
    organization_user=org_user,
    permissions=ORGANIZATION_USER_PERMISSION_ADMIN
)
```

## Testing

The implementation includes comprehensive test coverage:

- **Model Tests**: 13 tests in `backend/tests/baserow/core/test_organization_model.py`
  - CRUD operations
  - Business logic validation
  - Timestamp handling
  - Order management

- **API Tests**: 11 tests in `backend/tests/baserow/api/organizations/test_organization_views.py`
  - All API endpoints
  - Permission enforcement
  - Error handling
  - Edge cases

Run tests with:
```bash
cd backend
pytest tests/baserow/core/test_organization_model.py
pytest tests/baserow/api/organizations/test_organization_views.py
```

## Database Migration

The feature includes a migration file: `0108_organization_organizationuser.py`

Apply migrations with:
```bash
python manage.py migrate
```

## Future Enhancements

This minimal implementation provides a foundation for:

1. **Workspace Hierarchy**: Link workspaces to organizations
2. **Organization Settings**: Add organization-specific configuration
3. **Billing Integration**: Organization-level subscription management
4. **Team Management**: Advanced permission models and team structures
5. **Organization Invitations**: Invite users to organizations via email
6. **Organization Templates**: Pre-configured organization setups
7. **Audit Logs**: Track organization-level actions

## Files Changed

- `backend/src/baserow/core/models.py` - Added Organization and OrganizationUser models
- `backend/src/baserow/core/organization_handler.py` - Business logic handler (new file)
- `backend/src/baserow/core/exceptions.py` - Added organization-related exceptions
- `backend/src/baserow/core/migrations/0108_organization_organizationuser.py` - Database migration (new file)
- `backend/src/baserow/api/organizations/` - Complete API module (new directory)
- `backend/src/baserow/api/urls.py` - Integrated organization URLs
- `backend/tests/baserow/core/test_organization_model.py` - Model tests (new file)
- `backend/tests/baserow/api/organizations/test_organization_views.py` - API tests (new file)

## Security Considerations

- All API endpoints require authentication (`IsAuthenticated` permission)
- Business logic prevents orphaned organizations (last admin protection)
- Proper exception handling for all error cases
- No security vulnerabilities detected by CodeQL analysis
- Soft delete support prevents accidental data loss

## Compatibility

- Compatible with existing Baserow workspace structure
- Does not modify existing workspace functionality
- Can be extended without breaking changes
- Follows Baserow's existing patterns and conventions
