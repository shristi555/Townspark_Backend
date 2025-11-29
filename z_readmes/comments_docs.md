# Comment App

The Comment app handles comments on issues in the Townspark system. Users can comment on issues to provide additional information, ask questions, or discuss the issue.

## Overview

This app provides a complete comment management system with the following features:

- **Create Comments**: Any authenticated user can comment on any issue
- **List Comments**: View comments for a specific issue
- **Update Comments**: Only the comment owner can update their comment
- **Delete Comments**: Only the comment owner or admins can delete comments
- **Helper Endpoints**: Get user's own comments, comments by issue, or comments by specific user

## Comment Model

The Comment model represents a comment made on an issue.

### Fields

| Field        | Type          | Required | Description                       |
| ------------ | ------------- | -------- | --------------------------------- |
| `id`         | AutoField     | Auto     | Primary key                       |
| `issue`      | ForeignKey    | Yes      | The issue this comment relates to |
| `user`       | ForeignKey    | Auto     | User who made the comment         |
| `content`    | TextField     | Yes      | The content of the comment        |
| `created_at` | DateTimeField | Auto     | When the comment was created      |

---

## API Endpoints

Base URL: `/api/v1/`

### 1. Create Comment

**Endpoint:** `POST /api/v1/comments/new/`

Creates a new comment on an issue. Requires authentication.

#### Request

```http
POST /api/v1/comments/new/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
	"issue_id": 1,
	"content": "This is a sample comment."
}
```

| Field      | Type    | Required | Description                   |
| ---------- | ------- | -------- | ----------------------------- |
| `issue_id` | integer | Yes      | ID of the issue to comment on |
| `content`  | string  | Yes      | The content of the comment    |

#### Response

**Success (201 Created):**

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Sample Issue"
	},
	"user": {
		"id": 9,
		"email": "bruce.wayne@example.com"
	},
	"content": "This is a sample comment.",
	"created_at": "2024-01-01T12:00:00Z"
}
```

**Error (400 Bad Request):**

```json
{
	"issue_id": ["Issue with this ID does not exist."],
	"content": ["This field is required."]
}
```

**Error (401 Unauthorized):**

```json
{
	"detail": "Authentication credentials were not provided."
}
```

---

### 2. List Comments for Issue

**Endpoint:** `GET /api/v1/comments/list/{issue_id}/`

Lists all comments for a specific issue. Requires authentication.

#### Request

```http
GET /api/v1/comments/list/1/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**

```json
[
	{
		"id": 1,
		"issue": {
			"id": 1,
			"title": "Sample Issue"
		},
		"user": {
			"id": 9,
			"email": "bruce.wayne@example.com"
		},
		"content": "This is a sample comment.",
		"created_at": "2024-01-01T12:00:00Z"
	},
	{
		"id": 2,
		"issue": {
			"id": 1,
			"title": "Sample Issue"
		},
		"user": {
			"id": 10,
			"email": "clark.kent@example.com"
		},
		"content": "This is another sample comment.",
		"created_at": "2024-01-02T12:00:00Z"
	}
]
```

---

### 3. Update Comment

**Endpoint:** `PUT /api/v1/comments/update/{id}/` or `PATCH /api/v1/comments/update/{id}/`

Updates an existing comment. Requires authentication. **Only the user who created the comment can update it.**

#### Request

```http
PATCH /api/v1/comments/update/1/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
	"content": "Updated comment content."
}
```

| Field     | Type   | Required | Description     |
| --------- | ------ | -------- | --------------- |
| `content` | string | Yes      | Updated content |

#### Response

**Success (200 OK):**

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Sample Issue"
	},
	"user": {
		"id": 9,
		"email": "bruce.wayne@example.com"
	},
	"content": "Updated comment content.",
	"created_at": "2024-01-01T12:00:00Z"
}
```

**Error (403 Forbidden):**

```json
{
	"detail": "You do not have permission to update this comment."
}
```

---

### 4. Delete Comment

**Endpoint:** `DELETE /api/v1/comments/delete/{id}/`

Deletes a comment. Requires authentication. **Only the user who created the comment or an admin can delete it.**

#### Request

```http
DELETE /api/v1/comments/delete/1/
Authorization: Bearer <access_token>
```

#### Response

**Success (204 No Content):**

```json
{
	"message": "Comment deleted successfully."
}
```

**Error (403 Forbidden):**

```json
{
	"error": "You do not have permission to delete this comment."
}
```

---

## Helper Endpoints

### 5. Get My Comments

**Endpoint:** `GET /api/v1/comments/mine/`

Retrieves all comments made by the currently authenticated user. The user field is omitted in the response since it's always the authenticated user.

#### Request

```http
GET /api/v1/comments/mine/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**

```json
[
	{
		"id": 1,
		"issue": {
			"id": 1,
			"title": "Sample Issue"
		},
		"content": "This is a sample comment.",
		"created_at": "2024-01-01T12:00:00Z"
	},
	{
		"id": 3,
		"issue": {
			"id": 2,
			"title": "Another Issue"
		},
		"content": "This is another comment.",
		"created_at": "2024-01-02T12:00:00Z"
	}
]
```

---

### 6. List Comments by Issue

**Endpoint:** `GET /api/v1/comments/issue/{issue_id}/`

Retrieves all comments related to a specific issue. Same as the main list endpoint but with a different URL path.

#### Request

```http
GET /api/v1/comments/issue/1/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**

```json
[
	{
		"id": 1,
		"issue": {
			"id": 1,
			"title": "Sample Issue"
		},
		"user": {
			"id": 9,
			"email": "bruce.wayne@example.com"
		},
		"content": "This is a sample comment.",
		"created_at": "2024-01-01T12:00:00Z"
	}
]
```

---

### 7. List Comments by User

**Endpoint:** `GET /api/v1/comments/user/{user_id}/`

Retrieves all comments made by a specific user. **Only admins and staff can access this endpoint.**

#### Request

```http
GET /api/v1/comments/user/9/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK) - Staff/Admin only:**

```json
[
	{
		"id": 1,
		"issue": {
			"id": 1,
			"title": "Sample Issue"
		},
		"user": {
			"id": 9,
			"email": "bruce.wayne@example.com"
		},
		"content": "This is a sample comment.",
		"created_at": "2024-01-01T12:00:00Z"
	}
]
```

**Error (403 Forbidden) - Non-staff user:**

```json
{
	"error": "Only admins and staff can view comments by other users."
}
```

---

## Permissions Summary

| Endpoint          | Regular User | Staff       | Admin       |
| ----------------- | ------------ | ----------- | ----------- |
| Create Comment    | ✅           | ✅          | ✅          |
| List Comments     | ✅           | ✅          | ✅          |
| Update Comment    | ✅ Own only  | ✅ Own only | ✅ Own only |
| Delete Comment    | ✅ Own only  | ✅ Any      | ✅ Any      |
| My Comments       | ✅           | ✅          | ✅          |
| Comments by Issue | ✅           | ✅          | ✅          |
| Comments by User  | ❌           | ✅          | ✅          |

---

## Usage Examples

### cURL Examples

**Create a comment:**

```bash
curl -X POST http://localhost:8000/api/v1/comments/new/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": 1,
    "content": "This is a sample comment on the issue."
  }'
```

**List comments for an issue:**

```bash
curl -X GET http://localhost:8000/api/v1/comments/list/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Get my comments:**

```bash
curl -X GET http://localhost:8000/api/v1/comments/mine/ \
  -H "Authorization: Bearer <access_token>"
```

**Update a comment:**

```bash
curl -X PATCH http://localhost:8000/api/v1/comments/update/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated comment content."
  }'
```

**Delete a comment:**

```bash
curl -X DELETE http://localhost:8000/api/v1/comments/delete/1/ \
  -H "Authorization: Bearer <access_token>"
```

**List comments by user (staff/admin only):**

```bash
curl -X GET http://localhost:8000/api/v1/comments/user/9/ \
  -H "Authorization: Bearer <access_token>"
```

---

## File Structure

```
comment/
├── __init__.py
├── admin.py          # Admin configuration for Comment model
├── apps.py           # App configuration
├── models.py         # Comment model definition
├── serializers.py    # DRF serializers for Comment
├── urls.py           # URL routing
├── views.py          # API views
├── tests.py          # Test cases
└── migrations/       # Database migrations
    └── 0001_initial.py
```

---

## Related Apps

- **Accounts App**: Provides user authentication and user models
- **Issue App**: Provides the Issue model that comments are related to
- **Progress App**: Tracks progress updates for issues
- **Likes App**: Handles likes on issues

---

## Dependencies

- Django >= 4.0
- Django REST Framework
- djangorestframework-simplejwt (for authentication)
- Accounts app (for User model)
- Issue app (for Issue model)
