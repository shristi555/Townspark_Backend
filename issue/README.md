# Issue App

The Issue app handles the creation, management, and tracking of issues/complaints in the Townspark system. Users can create issues, and staff members can manage and resolve them.

## Overview

This app provides a complete issue management system with the following features:

- **Create Issues**: Any authenticated user can create issues
- **View Issues**: Users can view their own issues; staff can view all issues
- **Update Issues**: Users can update their own issues; staff can update any issue
- **Delete Issues**: Users can delete their own issues; staff can delete any issue
- **Status Management**: Staff can change issue status and mark issues as resolved

## Issue Model

The Issue model represents a complaint or issue submitted by users.

### Fields

| Field         | Type          | Required | Description                         |
| ------------- | ------------- | -------- | ----------------------------------- |
| `id`          | AutoField     | Auto     | Primary key                         |
| `title`       | CharField     | Yes      | Issue title (max 255 chars)         |
| `description` | TextField     | Yes      | Detailed description of the issue   |
| `status`      | CharField     | No       | Current status (default: "open")    |
| `created_at`  | DateTimeField | Auto     | When the issue was created          |
| `updated_at`  | DateTimeField | Auto     | When the issue was last updated     |
| `created_by`  | ForeignKey    | Auto     | User who created the issue          |
| `resolved_by` | ForeignKey    | No       | Staff member who resolved the issue |

### Status Values

| Status        | Description                   |
| ------------- | ----------------------------- |
| `open`        | Newly created issue (default) |
| `in_progress` | Issue is being worked on      |
| `resolved`    | Issue has been resolved       |
| `closed`      | Issue has been closed         |

---

## API Endpoints

Base URL: `/api/v1/`

### 1. Create Issue

**Endpoint:** `POST /api/v1/issues/new/`

Creates a new issue. Requires authentication.

#### Request

```http
POST /api/v1/issues/new/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
	"title": "Pothole on Main Street",
	"description": "There is a large pothole on Main Street near the intersection with Oak Avenue. It's causing damage to vehicles."
}
```

| Field         | Type   | Required | Description          |
| ------------- | ------ | -------- | -------------------- |
| `title`       | string | Yes      | Title of the issue   |
| `description` | string | Yes      | Detailed description |

#### Response

**Success (201 Created):**

```json
{
	"id": 1,
	"title": "Pothole on Main Street",
	"description": "There is a large pothole on Main Street near the intersection with Oak Avenue. It's causing damage to vehicles.",
	"status": "open",
	"created_at": "2024-01-01T12:00:00Z",
	"updated_at": "2024-01-01T12:00:00Z",
	"created_by": {
		"id": 9,
		"email": "bruce.wayne@example.com"
	},
	"resolved_by": null
}
```

**Error (400 Bad Request):**

```json
{
	"title": ["This field is required."],
	"description": ["This field is required."]
}
```

**Error (401 Unauthorized):**

```json
{
	"detail": "Authentication credentials were not provided."
}
```

---

### 2. List Issues

**Endpoint:** `GET /api/v1/issues/list/`

Lists issues based on user permissions. Requires authentication.

- **Regular users**: See only their own issues
- **Staff/Admin users**: See all issues

#### Request

```http
GET /api/v1/issues/list/
Authorization: Bearer <access_token>
```

**Optional Query Parameters:**

| Parameter | Type   | Description                                            |
| --------- | ------ | ------------------------------------------------------ |
| `status`  | string | Filter by status (open, in_progress, resolved, closed) |

**Example with filter:**

```http
GET /api/v1/issues/list/?status=open
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**

```json
[
	{
		"id": 1,
		"title": "Pothole on Main Street",
		"description": "There is a large pothole on Main Street near the intersection with Oak Avenue.",
		"status": "open",
		"created_at": "2024-01-01T12:00:00Z",
		"updated_at": "2024-01-01T12:00:00Z",
		"created_by": {
			"id": 9,
			"email": "bruce.wayne@example.com"
		},
		"resolved_by": null
	},
	{
		"id": 2,
		"title": "Broken Street Light",
		"description": "The street light at 123 Elm Street has been broken for a week.",
		"status": "in_progress",
		"created_at": "2024-01-02T12:00:00Z",
		"updated_at": "2024-01-03T12:00:00Z",
		"created_by": {
			"id": 10,
			"email": "clark.kent@example.com"
		},
		"resolved_by": null
	}
]
```

---

### 3. Retrieve Issue

**Endpoint:** `GET /api/v1/issues/detail/{id}/`

Retrieves a specific issue by ID. Requires authentication.

- **Regular users**: Can only view their own issues
- **Staff/Admin users**: Can view any issue

#### Request

```http
GET /api/v1/issues/detail/1/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**

```json
{
	"id": 1,
	"title": "Pothole on Main Street",
	"description": "There is a large pothole on Main Street near the intersection with Oak Avenue. It's causing damage to vehicles.",
	"status": "open",
	"created_at": "2024-01-01T12:00:00Z",
	"updated_at": "2024-01-01T12:00:00Z",
	"created_by": {
		"id": 9,
		"email": "bruce.wayne@example.com"
	},
	"resolved_by": null
}
```

**Error (403 Forbidden):**

```json
{
	"error": "You do not have permission to view this issue."
}
```

**Error (404 Not Found):**

```json
{
	"detail": "Not found."
}
```

---

### 4. Update Issue

**Endpoint:** `PUT /api/v1/issues/update/{id}/` or `PATCH /api/v1/issues/update/{id}/`

Updates an existing issue. Requires authentication.

- **Regular users**: Can update their own issues (title, description only)
- **Staff/Admin users**: Can update any issue including status

#### Request

```http
PUT /api/v1/issues/update/1/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Full Update (PUT):**

```json
{
	"title": "Pothole on Main Street - Updated",
	"description": "Updated description with more details.",
	"status": "in_progress"
}
```

**Partial Update (PATCH):**

```json
{
	"status": "resolved"
}
```

| Field         | Type   | Required            | Description                                    |
| ------------- | ------ | ------------------- | ---------------------------------------------- |
| `title`       | string | PUT: Yes, PATCH: No | Issue title                                    |
| `description` | string | PUT: Yes, PATCH: No | Issue description                              |
| `status`      | string | No                  | Issue status (staff/admin only for "resolved") |

#### Response

**Success (200 OK):**

```json
{
	"id": 1,
	"title": "Pothole on Main Street - Updated",
	"description": "Updated description with more details.",
	"status": "resolved",
	"created_at": "2024-01-01T12:00:00Z",
	"updated_at": "2024-01-05T14:30:00Z",
	"created_by": {
		"id": 9,
		"email": "bruce.wayne@example.com"
	},
	"resolved_by": {
		"id": 5,
		"email": "staff.member@example.com"
	}
}
```

**Error (400 Bad Request) - Non-staff trying to resolve:**

```json
{
	"status": ["Only staff members can mark issues as resolved."]
}
```

**Error (403 Forbidden):**

```json
{
	"error": "You do not have permission to update this issue."
}
```

---

### 5. Delete Issue

**Endpoint:** `DELETE /api/v1/issues/delete/{id}/`

Deletes an issue. Requires authentication.

- **Regular users**: Can only delete their own issues
- **Staff/Admin users**: Can delete any issue

#### Request

```http
DELETE /api/v1/issues/delete/1/
Authorization: Bearer <access_token>
```

#### Response

**Success (204 No Content):**

```json
{
	"message": "Issue deleted successfully."
}
```

**Error (403 Forbidden):**

```json
{
	"error": "You do not have permission to delete this issue."
}
```

**Error (404 Not Found):**

```json
{
	"detail": "Not found."
}
```

---

## Permissions Summary

| Endpoint         | Regular User         | Staff               | Admin               |
| ---------------- | -------------------- | ------------------- | ------------------- |
| Create Issue     | ✅ Own issues        | ✅                  | ✅                  |
| List Issues      | ✅ Own issues only   | ✅ All issues       | ✅ All issues       |
| View Issue       | ✅ Own issues only   | ✅ Any issue        | ✅ Any issue        |
| Update Issue     | ✅ Own (title, desc) | ✅ Any (all fields) | ✅ Any (all fields) |
| Delete Issue     | ✅ Own issues only   | ✅ Any issue        | ✅ Any issue        |
| Mark as Resolved | ❌                   | ✅                  | ✅                  |

---

## Status Workflow

```
┌─────────┐
│  open   │ ◄─── New issue created
└────┬────┘
     │
     ▼
┌─────────────┐
│ in_progress │ ◄─── Staff starts working
└──────┬──────┘
       │
       ▼
┌──────────┐
│ resolved │ ◄─── Staff resolves issue (resolved_by set)
└────┬─────┘
     │
     ▼
┌────────┐
│ closed │ ◄─── Issue closed
└────────┘
```

**Note:** Issues can be reopened by changing status back to "open", which clears the `resolved_by` field.

---

## Usage Examples

### cURL Examples

**Create an issue:**

```bash
curl -X POST http://localhost:8000/api/v1/issues/new/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Broken sidewalk",
    "description": "The sidewalk on 5th Avenue is cracked and dangerous."
  }'
```

**List all issues:**

```bash
curl -X GET http://localhost:8000/api/v1/issues/list/ \
  -H "Authorization: Bearer <access_token>"
```

**List issues by status:**

```bash
curl -X GET "http://localhost:8000/api/v1/issues/list/?status=open" \
  -H "Authorization: Bearer <access_token>"
```

**Get issue details:**

```bash
curl -X GET http://localhost:8000/api/v1/issues/detail/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Update an issue (partial):**

```bash
curl -X PATCH http://localhost:8000/api/v1/issues/update/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

**Mark issue as resolved (staff only):**

```bash
curl -X PATCH http://localhost:8000/api/v1/issues/update/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved"
  }'
```

**Delete an issue:**

```bash
curl -X DELETE http://localhost:8000/api/v1/issues/delete/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

## File Structure

```
issue/
├── __init__.py
├── admin.py          # Admin configuration for Issue model
├── apps.py           # App configuration
├── models.py         # Issue model definition
├── serializers.py    # DRF serializers for Issue
├── urls.py           # URL routing
├── views.py          # API views
├── tests.py          # Test cases
└── migrations/       # Database migrations
    └── 0001_initial.py
```

---

## Related Apps

- **Accounts App**: Provides user authentication and user models
- **Progress App**: Tracks progress updates for issues
- **Comments App**: Handles comments on issues
- **Likes App**: Handles likes on issues

---

## Dependencies

- Django >= 4.0
- Django REST Framework
- djangorestframework-simplejwt (for authentication)
- Accounts app (for User model)
