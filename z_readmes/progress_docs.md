# Progress App

The Progress app tracks progress updates for issues in the Townspark system. Staff members can create progress updates to document the work being done on issues and update their status.

## Overview

This app provides a complete progress tracking system with the following features:

- **Create Progress Updates**: Staff members can create progress updates for issues
- **Track Status Changes**: Each progress update can change the issue's status
- **Attach Images**: Multiple images can be attached to document work done
- **View Progress History**: Users can view the progress history of their issues

## Models

### Progress Model

The Progress model represents a single progress update for an issue.

| Field        | Type          | Required | Description                                  |
| ------------ | ------------- | -------- | -------------------------------------------- |
| `id`         | AutoField     | Auto     | Primary key                                  |
| `issue`      | ForeignKey    | Yes      | The issue this progress update is related to |
| `status`     | CharField     | Yes      | The current status after this update         |
| `notes`      | TextField     | No       | Optional notes about this progress update    |
| `updated_at` | DateTimeField | Auto     | When this progress update was made           |
| `updated_by` | ForeignKey    | Auto     | The staff member who made this update        |

### ProgressImage Model

The ProgressImage model allows multiple images to be attached to a progress update.

| Field         | Type          | Required | Description                               |
| ------------- | ------------- | -------- | ----------------------------------------- |
| `id`          | AutoField     | Auto     | Primary key                               |
| `progress`    | ForeignKey    | Yes      | The progress update this image belongs to |
| `image`       | ImageField    | Yes      | The image file                            |
| `uploaded_at` | DateTimeField | Auto     | When the image was uploaded               |

### Status Values

| Status        | Description              |
| ------------- | ------------------------ |
| `open`        | Issue is open            |
| `in_progress` | Issue is being worked on |
| `resolved`    | Issue has been resolved  |
| `closed`      | Issue has been closed    |

---

## API Endpoints

Base URL: `/api/v1/`

### 1. Create Progress Update

**Endpoint:** `POST /api/v1/progress/new/`

Creates a new progress update. **Staff/Admin only**.

When a progress update is created, the related issue's status is automatically updated to match.

#### Request

```http
POST /api/v1/progress/new/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**JSON Request:**

```json
{
	"issue_id": 1,
	"status": "in_progress",
	"notes": "Started working on fixing the pothole. Equipment has been dispatched."
}
```

**Multipart Request (with images):**

```http
POST /api/v1/progress/new/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

issue_id: 1
status: in_progress
notes: Started working on fixing the pothole.
images: [file1.jpg, file2.jpg]
```

| Field      | Type    | Required | Description                                      |
| ---------- | ------- | -------- | ------------------------------------------------ |
| `issue_id` | integer | Yes      | ID of the issue to update                        |
| `status`   | string  | Yes      | New status (open, in_progress, resolved, closed) |
| `notes`    | string  | No       | Notes about this progress update                 |
| `images`   | file[]  | No       | Images documenting the progress                  |

#### Response

**Success (201 Created):**

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Pothole on Main Street"
	},
	"status": "in_progress",
	"notes": "Started working on fixing the pothole. Equipment has been dispatched.",
	"updated_at": "2024-01-02T10:00:00Z",
	"updated_by": {
		"id": 5,
		"email": "staff.member@example.com"
	},
	"images": [
		{
			"id": 1,
			"image": "http://localhost:8000/media/progress_images/issue_1/progress_1_1.jpg",
			"uploaded_at": "2024-01-02T10:00:00Z"
		}
	]
}
```

**Error (400 Bad Request):**

```json
{
	"issue_id": ["Issue not found."]
}
```

**Error (403 Forbidden):**

```json
{
	"detail": "You do not have permission to perform this action."
}
```

---

### 2. List Progress Updates

**Endpoint:** `GET /api/v1/progress/list/`

Lists progress updates based on user permissions. Requires authentication.

- **Regular users**: See progress for their own issues only
- **Staff/Admin users**: See all progress updates

#### Request

```http
GET /api/v1/progress/list/
Authorization: Bearer <access_token>
```

**Optional Query Parameters:**

| Parameter  | Type    | Description        |
| ---------- | ------- | ------------------ |
| `issue_id` | integer | Filter by issue ID |
| `status`   | string  | Filter by status   |

**Example with filters:**

```http
GET /api/v1/progress/list/?issue_id=1&status=in_progress
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
			"title": "Pothole on Main Street"
		},
		"status": "in_progress",
		"notes": "Started working on fixing the pothole.",
		"updated_at": "2024-01-02T10:00:00Z",
		"updated_by": {
			"id": 5,
			"email": "staff.member@example.com"
		},
		"images": []
	},
	{
		"id": 2,
		"issue": {
			"id": 1,
			"title": "Pothole on Main Street"
		},
		"status": "resolved",
		"notes": "Pothole has been filled and repaired.",
		"updated_at": "2024-01-03T15:00:00Z",
		"updated_by": {
			"id": 5,
			"email": "staff.member@example.com"
		},
		"images": [
			{
				"id": 1,
				"image": "http://localhost:8000/media/progress_images/issue_1/progress_2_1.jpg",
				"uploaded_at": "2024-01-03T15:00:00Z"
			}
		]
	}
]
```

---

### 3. Retrieve Progress Update

**Endpoint:** `GET /api/v1/progress/detail/{id}/`

Retrieves a specific progress update by ID. Requires authentication.

- **Regular users**: Can only view progress for their own issues
- **Staff/Admin users**: Can view any progress update

#### Request

```http
GET /api/v1/progress/detail/1/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Pothole on Main Street"
	},
	"status": "in_progress",
	"notes": "Started working on fixing the pothole. Equipment has been dispatched.",
	"updated_at": "2024-01-02T10:00:00Z",
	"updated_by": {
		"id": 5,
		"email": "staff.member@example.com"
	},
	"images": []
}
```

**Error (403 Forbidden):**

```json
{
	"error": "You do not have permission to view this progress update."
}
```

**Error (404 Not Found):**

```json
{
	"detail": "Not found."
}
```

---

### 4. Update Progress Update

**Endpoint:** `PUT /api/v1/progress/update/{id}/` or `PATCH /api/v1/progress/update/{id}/`

Updates an existing progress update. **Staff/Admin only**.

#### Request

```http
PATCH /api/v1/progress/update/1/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
	"status": "resolved",
	"notes": "Work completed. The pothole has been filled."
}
```

| Field    | Type   | Required | Description              |
| -------- | ------ | -------- | ------------------------ |
| `status` | string | No       | Updated status           |
| `notes`  | string | No       | Updated notes            |
| `images` | file[] | No       | Additional images to add |

#### Response

**Success (200 OK):**

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Pothole on Main Street"
	},
	"status": "resolved",
	"notes": "Work completed. The pothole has been filled.",
	"updated_at": "2024-01-02T10:00:00Z",
	"updated_by": {
		"id": 5,
		"email": "staff.member@example.com"
	},
	"images": []
}
```

**Error (403 Forbidden):**

```json
{
	"detail": "You do not have permission to perform this action."
}
```

---

### 5. Delete Progress Update

**Endpoint:** `DELETE /api/v1/progress/delete/{id}/`

Deletes a progress update. **Staff/Admin only**.

#### Request

```http
DELETE /api/v1/progress/delete/1/
Authorization: Bearer <access_token>
```

#### Response

**Success (204 No Content):**

```json
{
	"message": "Progress update deleted successfully."
}
```

**Error (403 Forbidden):**

```json
{
	"detail": "You do not have permission to perform this action."
}
```

**Error (404 Not Found):**

```json
{
	"detail": "Not found."
}
```

---

### 6. List Progress Updates by Issue

**Endpoint:** `GET /api/v1/progress/issue/{issue_id}/`

Lists all progress updates for a specific issue. Requires authentication.

- **Regular users**: Can only view progress for their own issues
- **Staff/Admin users**: Can view progress for any issue

#### Request

```http
GET /api/v1/progress/issue/1/
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
			"title": "Pothole on Main Street"
		},
		"status": "in_progress",
		"notes": "Started working on the issue.",
		"updated_at": "2024-01-02T10:00:00Z",
		"updated_by": {
			"id": 5,
			"email": "staff.member@example.com"
		},
		"images": []
	},
	{
		"id": 2,
		"issue": {
			"id": 1,
			"title": "Pothole on Main Street"
		},
		"status": "resolved",
		"notes": "Issue has been resolved.",
		"updated_at": "2024-01-03T15:00:00Z",
		"updated_by": {
			"id": 5,
			"email": "staff.member@example.com"
		},
		"images": [
			{
				"id": 1,
				"image": "http://localhost:8000/media/progress_images/issue_1/progress_2_1.jpg",
				"uploaded_at": "2024-01-03T15:00:00Z"
			}
		]
	}
]
```

**Error (403 Forbidden):**

```json
{
	"error": "You do not have permission to view progress for this issue."
}
```

---

## Permissions Summary

| Endpoint        | Regular User       | Staff  | Admin  |
| --------------- | ------------------ | ------ | ------ |
| Create Progress | ❌                 | ✅     | ✅     |
| List Progress   | ✅ Own issues only | ✅ All | ✅ All |
| View Progress   | ✅ Own issues only | ✅ Any | ✅ Any |
| Update Progress | ❌                 | ✅     | ✅     |
| Delete Progress | ❌                 | ✅     | ✅     |

---

## Progress Workflow

```
Issue Created (status: open)
        │
        ▼
┌──────────────────────────────────────┐
│  Staff creates Progress Update       │
│  status: "in_progress"               │
│  notes: "Started working..."         │
│  images: [before_photo.jpg]          │
└──────────────────────────────────────┘
        │
        │ Issue status auto-updated to "in_progress"
        ▼
┌──────────────────────────────────────┐
│  Staff creates Progress Update       │
│  status: "resolved"                  │
│  notes: "Work completed"             │
│  images: [after_photo.jpg]           │
└──────────────────────────────────────┘
        │
        │ Issue status auto-updated to "resolved"
        │ Issue resolved_by set to staff member
        ▼
    Issue Resolved
```

---

## Usage Examples

### cURL Examples

**Create a progress update (JSON):**

```bash
curl -X POST http://localhost:8000/api/v1/progress/new/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": 1,
    "status": "in_progress",
    "notes": "Started working on the issue."
  }'
```

**Create a progress update with images (multipart):**

```bash
curl -X POST http://localhost:8000/api/v1/progress/new/ \
  -H "Authorization: Bearer <access_token>" \
  -F "issue_id=1" \
  -F "status=in_progress" \
  -F "notes=Started working on the issue." \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg"
```

**List all progress updates:**

```bash
curl -X GET http://localhost:8000/api/v1/progress/list/ \
  -H "Authorization: Bearer <access_token>"
```

**List progress for a specific issue:**

```bash
curl -X GET http://localhost:8000/api/v1/progress/issue/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Get progress details:**

```bash
curl -X GET http://localhost:8000/api/v1/progress/detail/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Update a progress update:**

```bash
curl -X PATCH http://localhost:8000/api/v1/progress/update/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "notes": "Issue has been resolved."
  }'
```

**Delete a progress update:**

```bash
curl -X DELETE http://localhost:8000/api/v1/progress/delete/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

## File Structure

```
progress/
├── __init__.py
├── admin.py          # Admin configuration for Progress models
├── apps.py           # App configuration
├── models.py         # Progress and ProgressImage models
├── serializers.py    # DRF serializers
├── urls.py           # URL routing
├── views.py          # API views
├── tests.py          # Test cases
└── migrations/       # Database migrations
    └── 0001_initial.py
```

---

## Related Apps

- **Accounts App**: Provides user authentication and user models
- **Issue App**: Provides the Issue model that progress updates are linked to
- **Comments App**: Handles comments on issues
- **Likes App**: Handles likes on issues

---

## Dependencies

- Django >= 4.0
- Django REST Framework
- djangorestframework-simplejwt (for authentication)
- Pillow (for image handling)
- Accounts app (for User model)
- Issue app (for Issue model)
