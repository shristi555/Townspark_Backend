## Accounts App

This is the Accounts app, which handles user authentication, registration, and profile management for the project. It includes features such as login, logout, password reset, and user profile editing.

It uses djoser for token-based authentication and provides endpoints for user-related operations.

### Features

- Consistent response mechanism using a custom response utility
- User registration and authentication using djoser
- Token-based authentication with JWT
- Custom user model with profile image support
- Email-based authentication (no username required)

---

## API Endpoints
the following are the main API endpoints provided by the Accounts app, along with their expected request and response formats.

1. `POST /auth/users/` - User Registration
2. `POST /auth/login/` - User Login (Token Creation)
3. `POST /auth/jwt/refresh/` - Token Refresh
4. `POST /auth/jwt/verify/` - Token Verification
5. `GET /auth/users/me/` - Get Current User Profile
6. `PUT /auth/users/me/` or `PATCH /auth/users/me/` - Update Current User Profile

---

### 1. User Registration

**Endpoint:** `POST /auth/users/`

**Description:** Creates a new user account with email-based authentication.

**Expected Request Data:**

```json
{
  "email": "bruce.wyane@example.com",
  "password": "123@J456789",
  "full_name": "Bruce Wayne",
  "phone_number": "+9700123456",
  "address": "Wayne Manor, Gotham City",
}
```

**Expected Outcome (Success - 201):**

```json
{
	"success": true,
	"response": {
            "id": 9,
            "email": "bruce.wyane@example.com",
            "full_name": "Bruce Wayne",
            "phone_number": "+9700",
            "address": "Wayne Manor, Gotham City",
            "profile_image": null
        }
}
```

**Expected Outcome (Error - 400):**

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "An error occurred",
        "details": {
            "email": [
                "user with this email already exists."
            ],
            "phone_number": [
                "Phone number must be between 7-13 digits",
                "Phone number can only contain digits or a plus sign.",
                "Phone number must not contain consecutive special characters."
            ]
        }
    }
}
```

**Developer Tips:**

- Use `multipart/form-data` content type when uploading profile images
- Password is write-only and won't be returned in responses
- Email must be unique across all users

---

### 2. User Login (Token Creation)

**Endpoint:** `POST /auth/login/`

**Description:** Authenticates a user and returns JWT access and refresh tokens along with the user info of the user.

**Expected Request Data:**

```json
{
	"email": "bruce.wyane@example.com",
	"password": "securePassword123"
}
```

**Expected Outcome (Success - 200):**

```json
{
    "success": true,
    "response": {
        "tokens": {
            "refresh": "eyJhbGciOiJIUzI1N...",
            "access": "eyJhbGciOiJIUzI1Ni..."
        },
        "user": {
            "id": 9,
            "email": "bruce.wyane@example.com",
            "full_name": "Bruce Wayne",
            "phone_number": "+9700",
            "address": "Wayne Manor, Gotham City",
            "profile_image": null
        }
    },
    "error": null
}
```

**Expected Outcome (Error - 401):**

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "Email does not exist",
        "details": {
            "email": "No account found with the provided email"
        }
    }
}
```

**Response format description:**
In case of error response, 
- the "error" key contains the error details, while the "response" key is null.
- the details will be a key value pair where key is the field name and value is the error message.
- the "message" key provides a general description of the error.


**Developer Tips:**

- Store the access token for authenticated requests
- Store the refresh token to obtain new access tokens
- Access tokens typically expire faster than refresh tokens

---

### 3. Token Refresh

**Endpoint:** `POST /auth/jwt/refresh/`

**Description:** Obtains a new access token using a valid refresh token.

**Expected Request Data:**

```json
{
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Expected Outcome (Success - 200):**

```json
{
	"success": true,
	"response": {
		"access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
	}
}
```

**Expected Outcome (Error - 401):**

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "Token is invalid",
        "details": {
            "detail": "Token is invalid",
            "code": "token_not_valid"
        }
    }
}
```

**Developer Tips:**

- Call this endpoint before the access token expires
- Implement token refresh logic in your frontend interceptors

---

### 4. Token Verification

**Endpoint:** `POST /auth/jwt/verify/`

**Description:** Verifies if a given token is valid and not expired.

**Expected Request Data:**

```json
{
	"token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Expected Outcome (Success - 200):**

```json
{
    "success": true,
    "response": {},
    "error": null
}
```

**Expected Outcome (Error - 401):**

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "Token is invalid",
        "details": {
            "detail": "Token is invalid",
            "code": "token_not_valid"
        }
    }
}
```

**Developer Tips:**

- Use this to check token validity before making authenticated requests
- Useful for session validation on app startup

---

### 5. Get Current User Profile

**Endpoint:** `GET /auth/users/me/`

**Description:** Retrieves the authenticated user's profile information.

**Expected Request Headers:**

```
Authorization: Bearer <access_token>
```

**Expected Request Data:** None (GET request)

**Expected Outcome (Success - 200):**

```json
{
    "success": true,
    "response": {
        "id": 9,
        "email": "bruce.wjmjakjyne@example.com",
        "full_name": "Bruce Wayne",
        "phone_number": "+9700",
        "address": "Wayne Manor, Gotham City",
        "profile_image": null
    },
    "error": null
}
```

**Expected Outcome (Error - 401):**

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "Authentication credentials were not provided.",
        "details": {
            "detail": "Authentication credentials were not provided."
        }
    }
}
```

**Developer Tips:**

- Always include the Authorization header with Bearer token
- Profile image returns absolute URL for easy frontend integration
- Use this endpoint to fetch user data after login

---

### 6. Update Current User Profile

**Endpoint:** `PUT /auth/users/me/` or `PATCH /auth/users/me/`

**Description:** Updates the authenticated user's profile information.

**Expected Request Headers:**

```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data  // when updating profile_image
Content-Type: application/json    // for other fields
```

**Expected Request Data:**

```json
{
  "email": "bruce.wyane@example.com", // Email cannot be changed
  "password": "123@J456789", // New password to update
  "full_name": "Bruce Wayne Edited", // New name to update
  "phone_number": "+9700123456", 
  "address": "Wayne Manor, Gotham City",
    "profile_image": <file> // optional, file upload (use multipart/form-data)
}
```

**Expected Outcome (Success - 200):**

```json
{
    "success": true,
    "response": {
        "id": 9,
        "email": "bruce.wyane@example.com",
        "full_name": "Bruce Wayne edited",
        "phone_number": "+9700123456",
        "address": "Wayne Manor, Gotham City",
        "profile_image": null
    },
    "error": null
}
```

**Developer Tips:**

- Use `PATCH` for partial updates, `PUT` for full updates
- Email cannot be changed through this endpoint (it's the unique identifier)
- When updating profile image, old image is replaced

---

## Response Mechanism

The app uses a custom response structure to ensure consistent API responses across all endpoints. 
The response is always structured in JSON format and includes the following keys:

### Response Keys:

1. **success** (boolean) - Indicates whether the request was successful or not. This key is always present in every response.

2. **response** (object) - Contains the actual response data when the request is successful.(It is always present but can be null in error responses)

3. **error** (object) - Contains error details when the request fails. Only present on failed requests.

### Success Response (2xx)

```json
{
	"success": true,
	"response": {
		// actual response data
	}
}
```

### Error Response (4xx/5xx)

```json
{
	"success": false,
	"error": {
		"name": "error_name",
		"message": "Error description",
		"details": "Additional error details"
	},
    "response": null // but it is not 100% guranteed to be null even in error responses
}
```

[//]: # ()
[//]: # (### Response Utility Functions &#40;For Developers&#41;)

[//]: # (The following is the code snippet for the response utility functions used to generate consistent responses:)

[//]: # ()
[//]: # ()
[//]: # (```python)

[//]: # (# Success response with data and status code)

[//]: # (def success_response&#40;data, status=200&#41;:)

[//]: # (    return Response&#40;{"success": True, "response": data}, status=status&#41;)

[//]: # ()
[//]: # (# Error response with message, details, error name, and status code)

[//]: # (def error_response&#40;message, details="", error_name="error", status=400&#41;:)

[//]: # (    return Response&#40;)

[//]: # (        {)

[//]: # (            "success": False,)

[//]: # (            "error": {"name": error_name, "message": message, "details": details},)

[//]: # (        },)

[//]: # (        status=status,)

[//]: # (    &#41;)

[//]: # (```)

---

## Working with the User Model (For Developers)

The app uses a custom User model that extends Django's built-in AbstractBaseUser and PermissionsMixin. This allows for email-based authentication and additional profile fields.


### Current Model Structure

The custom `User` model extends Django's `AbstractBaseUser` and `PermissionsMixin` with the following fields:

- **email** (EmailField, unique, required) - Primary authentication field
- **full_name** (CharField, required) - User's full name
- **phone_number** (CharField, optional) - Contact number
- **address** (TextField, optional) - Physical address
- **profile_image** (ImageField, optional) - Profile picture
- **is_active** (BooleanField, default=True) - Account status
- **is_staff** (BooleanField, default=False) - Admin access

### Adding New Fields to the User Model

To add new fields to the User model:

1. **Add the field to the model** (`accounts/models.py`):

```python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    # ...existing fields...

    # New field example - optional field
    date_of_birth = models.DateField(blank=True, null=True)

    # New field example - required field
    country = models.CharField(max_length=100, default='Unknown')

    # New field example - with choices
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
```

2. **Update the serializers** (`accounts/serializers.py`):

```python
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from .models import User

class UserCreateSerializer(BaseUserCreateSerializer):
    # Add new fields here
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    country = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, required=False, allow_null=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "password",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
            "date_of_birth",  # new field
            "country",  # new field
            "gender",  # new field
        )

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
            "date_of_birth",  # new field
            "country",  # new field
            "gender",  # new field
        )
```

3. **Run migrations**:

```bash
python manage.py makemigrations
python manage.py migrate
```
**If using UV (Which is highly recommended):**

```bash
uv run manage.py makemigrations
uv run manage.py migrate
```

### Field Options Guide

**Making fields optional:**

- Add `blank=True, null=True` to the model field
- Set `required=False` in the serializer

**Making fields required:**

- Remove `blank=True, null=True` from model (or add `blank=False`)
- Set `required=True` in the serializer or add to `REQUIRED_FIELDS`

**Adding default values:**

- Add `default='value'` to the model field

**Adding validation:**

- Use Django's built-in validators or create custom ones
- Add validation in the serializer's `validate_<field_name>` method

### Developer Tips

1. **Using the User model in other apps:**

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a user
user = User.objects.create_user(
    email='test@example.com',
    password='password123',
    full_name='Test User'
)

# Get user by email
user = User.objects.get(email='test@example.com')

# Update user
user.full_name = 'Updated Name'
user.save()
```

2. **Profile image handling:**

- Images are automatically stored in `media/profile_images/user_<id>.<ext>`
- The `save()` method is overridden to ensure ID exists before saving images
- Old images are replaced when uploading new ones

3. **Authentication:**

- Login uses `email` instead of username
- `USERNAME_FIELD = "email"` configures this
- Password is automatically hashed by `set_password()`

4. **Admin access:**

- Set `is_staff=True` to give admin panel access
- Set `is_superuser=True` for full admin permissions

---

## Testing the API

### Using cURL

```bash
# Register a user
curl -X POST http://localhost:8000/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Get user profile
curl -X GET http://localhost:8000/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Using Postman or Thunder Client

1. Set the request method (GET, POST, PUT, PATCH)
2. Add the endpoint URL
3. For authenticated requests, add header: `Authorization: Bearer <token>`
4. For file uploads, use `form-data` body type
5. Check the response structure matches the expected format

---

## Troubleshooting

**Issue:** "User with this email already exists"

- Solution: Email must be unique. Use a different email or delete the existing user.

**Issue:** "Authentication credentials were not provided"

- Solution: Include the `Authorization: Bearer <token>` header in your request.

**Issue:** "Token is invalid or expired"

- Solution: Refresh your access token using the `/auth/jwt/refresh/` endpoint.

**Issue:** Profile image not uploading

- Solution: Ensure `Content-Type: multipart/form-data` is set and file is in correct format.

**Issue:** Migrations failing after adding new fields

- Solution: Provide default values for new required fields or make them optional.
