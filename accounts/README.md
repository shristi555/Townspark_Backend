# Accounts App

The Accounts app is the central module for user management and authentication in the Townspark Backend. It handles user registration, login, token management, and profile operations.

## Overview

This app provides a complete authentication system with three user levels:

| User Level       | Description       | Permissions                                   |
| ---------------- | ----------------- | --------------------------------------------- |
| **Admin**        | Top-level user    | Can manage all users and has full permissions |
| **Staff**        | Mid-level user    | Can manage issues and progress                |
| **Regular User** | Bottom-level user | Can create issues and view their progress     |

## User Model

The custom User model uses email as the unique identifier instead of username.

### Fields

| Field           | Type          | Required | Description                               |
| --------------- | ------------- | -------- | ----------------------------------------- |
| `id`            | AutoField     | Auto     | Primary key                               |
| `email`         | EmailField    | Yes      | Unique email address (used for login)     |
| `password`      | CharField     | Yes      | Hashed password                           |
| `full_name`     | CharField     | No       | User's full name                          |
| `phone_number`  | CharField     | No       | Phone number (7-13 digits, can include +) |
| `address`       | TextField     | No       | User's address                            |
| `profile_image` | ImageField    | No       | Profile picture                           |
| `is_active`     | BooleanField  | No       | Account status (default: True)            |
| `is_staff`      | BooleanField  | No       | Staff member status (default: False)      |
| `is_admin`      | BooleanField  | No       | Admin status (default: False)             |
| `date_joined`   | DateTimeField | Auto     | Account creation timestamp                |

### Public Fields

Only the following fields are exposed in public profile lookups:

- `full_name`
- `address`
- `profile_image`

---

## API Endpoints

Base URL: `/api/v1/`

### 1. User Registration

**Endpoint:** `POST /api/v1/auth/signup/`

Creates a new user account.

#### Request

```http
POST /api/v1/auth/signup/
Content-Type: application/json
```

```json
{
	"email": "bruce.wayne@example.com",
	"password": "secretpassword123",
	"full_name": "Bruce Wayne",
	"phone_number": "+9700123456",
	"address": "Wayne Manor, Gotham City"
}
```

| Field           | Type   | Required | Description                         |
| --------------- | ------ | -------- | ----------------------------------- |
| `email`         | string | Yes      | Valid email address                 |
| `password`      | string | Yes      | Minimum 8 characters                |
| `full_name`     | string | No       | User's full name                    |
| `phone_number`  | string | No       | Phone number (7-13 digits)          |
| `address`       | string | No       | User's address                      |
| `profile_image` | file   | No       | Profile image (multipart/form-data) |

#### Response

**Success (201 Created):**

```json
{
	"id": 9,
	"email": "bruce.wayne@example.com",
	"full_name": "Bruce Wayne",
	"phone_number": "+9700123456",
	"address": "Wayne Manor, Gotham City",
	"profile_image": null
}
```

**Error (400 Bad Request):**

```json
{
	"email": ["user with this email already exists."],
	"password": ["This field is required."]
}
```

---

### 2. User Login

**Endpoint:** `POST /api/v1/auth/login/`

Authenticates a user and returns JWT tokens along with user information.

#### Request

```http
POST /api/v1/auth/login/
Content-Type: application/json
```

```json
{
	"email": "bruce.wayne@example.com",
	"password": "secretpassword123"
}
```

| Field      | Type   | Required | Description              |
| ---------- | ------ | -------- | ------------------------ |
| `email`    | string | Yes      | Registered email address |
| `password` | string | Yes      | User's password          |

#### Response

**Success (200 OK):**

```json
{
	"tokens": {
		"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMzA1MDAwMCwiaWF0IjoxNzMyNDQ1MjAwLCJqdGkiOiJhYmNkZWYxMjM0NTYiLCJ1c2VyX2lkIjo5fQ.xxxxx",
		"access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyNTMxNjAwLCJpYXQiOjE3MzI0NDUyMDAsImp0aSI6IjEyMzQ1NmFiY2RlZiIsInVzZXJfaWQiOjl9.xxxxx"
	},
	"user": {
		"id": 9,
		"email": "bruce.wayne@example.com",
		"full_name": "Bruce Wayne",
		"phone_number": "+9700123456",
		"address": "Wayne Manor, Gotham City",
		"profile_image": null
	}
}
```

**Error - Email Not Found (400 Bad Request):**

```json
{
	"error": "Email does not exist",
	"details": {
		"email": "No account found with the provided email"
	}
}
```

**Error - Inactive Account (400 Bad Request):**

```json
{
	"error": "Account is inactive",
	"details": {
		"email": "The account associated with this email is inactive. Please contact support."
	}
}
```

**Error - Invalid Password (400 Bad Request):**

```json
{
	"error": "Invalid password",
	"details": {
		"password": "The provided password is incorrect for given email."
	}
}
```

---

### 3. Token Refresh

**Endpoint:** `POST /api/v1/auth/jwt/refresh/`

Refreshes the access token using a valid refresh token.

#### Request

```http
POST /api/v1/auth/jwt/refresh/
Content-Type: application/json
```

```json
{
	"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMzA1MDAwMCwiaWF0IjoxNzMyNDQ1MjAwLCJqdGkiOiJhYmNkZWYxMjM0NTYiLCJ1c2VyX2lkIjo5fQ.xxxxx"
}
```

| Field     | Type   | Required | Description         |
| --------- | ------ | -------- | ------------------- |
| `refresh` | string | Yes      | Valid refresh token |

#### Response

**Success (200 OK):**

```json
{
	"access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyNjE4MDAwLCJpYXQiOjE3MzI1MzE2MDAsImp0aSI6Im5ld3Rva2VuMTIzIiwidXNlcl9pZCI6OX0.xxxxx",
	"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMzEzNjQwMCwiaWF0IjoxNzMyNTMxNjAwLCJqdGkiOiJuZXdyZWZyZXNoMTIzIiwidXNlcl9pZCI6OX0.xxxxx"
}
```

**Error - Invalid Token (401 Unauthorized):**

```json
{
	"detail": "Token is invalid or expired",
	"code": "token_not_valid"
}
```

---

### 4. Token Verification

**Endpoint:** `POST /api/v1/auth/jwt/verify/`

Verifies if a token is valid.

#### Request

```http
POST /api/v1/auth/jwt/verify/
Content-Type: application/json
```

```json
{
	"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyNTMxNjAwLCJpYXQiOjE3MzI0NDUyMDAsImp0aSI6IjEyMzQ1NmFiY2RlZiIsInVzZXJfaWQiOjl9.xxxxx"
}
```

| Field   | Type   | Required | Description         |
| ------- | ------ | -------- | ------------------- |
| `token` | string | Yes      | JWT token to verify |

#### Response

**Success (200 OK):**

```json
{}
```

**Error - Invalid Token (401 Unauthorized):**

```json
{
	"detail": "Token is invalid or expired",
	"code": "token_not_valid"
}
```

---

### 5. Get Current User Profile

**Endpoint:** `GET /api/v1/auth/users/me/`

Retrieves the profile of the currently authenticated user.

#### Request

```http
GET /api/v1/auth/users/me/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**

```json
{
	"id": 9,
	"email": "bruce.wayne@example.com",
	"full_name": "Bruce Wayne",
	"phone_number": "+9700123456",
	"address": "Wayne Manor, Gotham City",
	"profile_image": "http://localhost:8000/media/profile_images/user_9.jpg"
}
```

**Error - Unauthorized (401 Unauthorized):**

```json
{
	"detail": "Authentication credentials were not provided."
}
```

---

### 6. Update Current User Profile

**Endpoint:** `PUT /api/v1/auth/users/me/` or `PATCH /api/v1/auth/users/me/`

Updates the profile of the currently authenticated user.

- `PUT` - Full update (all editable fields required)
- `PATCH` - Partial update (only provided fields are updated)

#### Request

```http
PATCH /api/v1/auth/users/me/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
	"full_name": "Bruce Wayne Edited",
	"phone_number": "+9700999888",
	"address": "New Wayne Manor, Gotham City"
}
```

| Field           | Type   | Required | Description                         |
| --------------- | ------ | -------- | ----------------------------------- |
| `full_name`     | string | No\*     | User's full name                    |
| `phone_number`  | string | No\*     | Phone number (7-13 digits)          |
| `address`       | string | No\*     | User's address                      |
| `profile_image` | file   | No\*     | Profile image (multipart/form-data) |

\*For PUT requests, all fields should be provided. For PATCH requests, only the fields to update are required.

#### Response

**Success (200 OK):**

```json
{
	"id": 9,
	"email": "bruce.wayne@example.com",
	"full_name": "Bruce Wayne Edited",
	"phone_number": "+9700999888",
	"address": "New Wayne Manor, Gotham City",
	"profile_image": "http://localhost:8000/media/profile_images/user_9.jpg"
}
```

**Error - Validation Error (400 Bad Request):**

```json
{
	"phone_number": ["Phone number must be between 7-13 digits"]
}
```

---

## Authentication

This app uses JWT (JSON Web Tokens) for authentication.

### Token Configuration

| Setting                  | Value  | Description                            |
| ------------------------ | ------ | -------------------------------------- |
| Access Token Lifetime    | 1 day  | Token used for API requests            |
| Refresh Token Lifetime   | 7 days | Token used to obtain new access tokens |
| Rotate Refresh Tokens    | Yes    | New refresh token issued on refresh    |
| Blacklist After Rotation | Yes    | Old refresh tokens are invalidated     |

### Using Authentication

Include the access token in the `Authorization` header for protected endpoints:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Refresh Flow

1. When the access token expires, send the refresh token to `/api/v1/auth/jwt/refresh/`
2. Receive new access and refresh tokens
3. Use the new access token for subsequent requests
4. Store the new refresh token for future refreshes

---

## Error Handling

All error responses follow a consistent format:

### Validation Errors

```json
{
	"field_name": ["Error message 1", "Error message 2"]
}
```

### Authentication Errors

```json
{
	"detail": "Error description",
	"code": "error_code"
}
```

### Custom Error Format (Login)

```json
{
	"error": "Human-readable error title",
	"details": {
		"field": "Detailed error message"
	}
}
```

---

## Usage Examples

### cURL Examples

**Register a new user:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "mypassword123",
    "full_name": "Test User"
  }'
```

**Login:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "mypassword123"
  }'
```

**Get current user profile:**

```bash
curl -X GET http://localhost:8000/api/v1/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

**Update profile:**

```bash
curl -X PATCH http://localhost:8000/api/v1/auth/users/me/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name"
  }'
```

**Upload profile image:**

```bash
curl -X PATCH http://localhost:8000/api/v1/auth/users/me/ \
  -H "Authorization: Bearer <access_token>" \
  -F "profile_image=@/path/to/image.jpg"
```

---

## File Structure

```
accounts/
├── __init__.py
├── admin.py          # Admin configuration for User model
├── apps.py           # App configuration
├── models.py         # User model definition
├── serializers.py    # DRF serializers for User
├── urls.py           # URL routing
├── views.py          # API views
├── tests.py          # Test cases
└── migrations/       # Database migrations
```

---

## Dependencies

- Django >= 4.0
- Django REST Framework
- djangorestframework-simplejwt
- Pillow (for image handling)
