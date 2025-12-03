# Issue App

This app handles issue reporting, categorization, and management within the TownSpark platform.

## Models

### Category

Represents different categories of issues (e.g., potholes, streetlight outages).

| Field       | Type           | Description                        |
| ----------- | -------------- | ---------------------------------- |
| id          | AutoField      | Unique identifier (auto-generated) |
| name        | CharField(100) | Name of the category               |
| description | TextField      | Brief description of the category  |

### Issue

Represents an individual issue reported by a user, linked to a category.

| Field       | Type                 | Description                                 |
| ----------- | -------------------- | ------------------------------------------- |
| id          | AutoField            | Unique identifier (auto-generated)          |
| title       | CharField(255)       | Title of the issue                          |
| description | TextField            | Detailed description of the issue           |
| location    | CharField(500)       | Location where the issue was observed       |
| status      | CharField(20)        | Status: open, in_progress, resolved, closed |
| created_at  | DateTimeField        | Timestamp when created (auto)               |
| updated_at  | DateTimeField        | Timestamp when updated (auto)               |
| category    | ForeignKey(Category) | Category of the issue                       |
| reported_by | ForeignKey(User)     | User who reported the issue                 |

### IssueImage

Stores multiple images associated with an issue.

| Field       | Type              | Description                        |
| ----------- | ----------------- | ---------------------------------- |
| id          | AutoField         | Unique identifier (auto-generated) |
| issue       | ForeignKey(Issue) | Related issue                      |
| image       | ImageField        | Image file                         |
| uploaded_at | DateTimeField     | Upload timestamp (auto)            |

## API Endpoints

### Issue Endpoints

| Method | Endpoint                            | Description                     | Auth Required              |
| ------ | ----------------------------------- | ------------------------------- | -------------------------- |
| POST   | `/api/v1/issues/new/`               | Create a new issue              | Yes                        |
| GET    | `/api/v1/issues/list/`              | List all issues                 | Yes                        |
| GET    | `/api/v1/issues/info/<issue_id>/`   | Get specific issue details      | Yes                        |
| GET    | `/api/v1/issues/user/<user_id>/`    | Get user's reported issues      | Yes                        |
| GET    | `/api/v1/issues/my/`                | Get authenticated user's issues | Yes                        |
| PATCH  | `/api/v1/issues/update/<issue_id>/` | Update issue status             | Yes (reporter/admin/staff) |
| DELETE | `/api/v1/issues/delete/<issue_id>/` | Delete an issue                 | Yes (reporter/admin)       |

### Category Endpoints

| Method | Endpoint                   | Description           | Auth Required    |
| ------ | -------------------------- | --------------------- | ---------------- |
| GET    | `/api/v1/categories/list/` | List all categories   | No               |
| POST   | `/api/v1/categories/new/`  | Create a new category | Yes (admin only) |

## Permissions

- **IsAdmin**: Only admin users (is_admin=True)
- **IsStaff**: Only staff users (is_staff=True)
- **IsAdminOrStaff**: Admin or staff users
- **IsReporterOrAdminOrStaff**: Reporter of the issue, admin, or staff

## Response Format

All responses follow the SER (Success, Error, Response) format:

```json
{
    "success": true,
    "response": { ... },
    "error": null
}
```

## Usage Examples

### Create an Issue

```bash
POST /api/v1/issues/new/
{
    "title": "Pothole on Main St.",
    "description": "Large pothole causing vehicle damage.",
    "location": "Main St. near 1st Ave.",
    "category": 1
}
```

### Update Issue Status

```bash
PATCH /api/v1/issues/update/1/
{
    "status": "in_progress"
}
```

### Create a Category (Admin Only)

```bash
POST /api/v1/categories/new/
{
    "name": "Streetlight Outages",
    "description": "Issues related to streetlight outages."
}
```

## Test Cases

Run tests with:

```bash
uv run pytest issue/tests.py -v
```

The test suite covers:

- Issue creation
- Issue listing and filtering
- Issue detail retrieval
- User reported issues
- Issue status updates by different user roles
- Category listing and creation
- Permission enforcement

# Endpoint Documentation for Progress App

## Creating new issue

POST /api/v1/issues/new/

### Example Request

```
{
	"title": "Test Issue",
	"description": "This is a test issue description.",
	"location": "Test Location",
	"category": 1
}
```

### Issue creation response:

```json
{
	"success": true,
	"response": {
		"id": 1,
		"title": "Test Issue",
		"description": "This is a test issue description.",
		"location": "Test Location",
		"images": [],
		"status": "open",
		"created_at": "2025-12-03T10:22:07Z",
		"updated_at": "2025-12-03T10:22:07Z",
		"category": {
			"id": 1,
			"name": "Potholes",
			"description": "Issues related to potholes on roads."
		},
		"reported_by": {
			"id": 1,
			"full_name": "Regular User",
			"profile_image": null
		}
	},
	"error": null
}
```

## Listing issues

GET /api/v1/issues/list/

### Issue list response:

```json
{
	"success": true,
	"response": [
		{
			"id": 1,
			"title": "Test Pothole",
			"location": "Main St. near 1st Ave.",
			"status": "open",
			"created_at": "2025-12-03T10:22:08Z",
			"updated_at": "2025-12-03T10:22:08Z",
			"category": {
				"id": 1,
				"name": "Potholes",
				"description": "Issues related to potholes on roads."
			},
			"reported_by": {
				"id": 1,
				"full_name": "Regular User",
				"profile_image": null
			},
			"image_count": 0
		}
	],
	"error": null
}
```

## Issue details retrieval

GET /api/v1/issues/info/<issue_id>/

### Issue detail response:

```json
{
	"success": true,
	"response": {
		"id": 1,
		"title": "Test Pothole",
		"description": "There is a large pothole on Main St.",
		"location": "Main St. near 1st Ave.",
		"images": [],
		"status": "open",
		"created_at": "2025-12-03T10:22:09Z",
		"updated_at": "2025-12-03T10:22:09Z",
		"category": {
			"id": 1,
			"name": "Potholes",
			"description": "Issues related to potholes on roads."
		},
		"reported_by": {
			"id": 1,
			"full_name": "Regular User",
			"profile_image": null
		}
	},
	"error": null
}
```

in case of failure or issue dont exists:

### Issue not found response:

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "No Issue matches the given query.",
		"details": {
			"detail": "No Issue matches the given query."
		}
	}
}
```

## Issue Progress

GET /api/v1/progress/issue/<issue_id>/

### Issue progress list response:

```json
{
	"success": true,
	"response": [
		{
			"id": 1,
			"issue": 1,
			"description": "Progress update 1",
			"created_at": "2025-12-03T10:22:18Z",
			"updated_by": {
				"id": 1,
				"full_name": "Regular User"
			},
			"images": []
		},
		{
			"id": 2,
			"issue": 1,
			"description": "Progress update 2",
			"created_at": "2025-12-03T10:22:18Z",
			"updated_by": {
				"id": 1,
				"full_name": "Regular User",
				"profile_image": null
			},
			"images": []
		}
	],
	"error": null
}
```
