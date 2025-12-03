# Profile App

This app handles user profile management within the TownSpark platform, providing endpoints to view and update user profiles with statistics.

## Features

- Get authenticated user's profile with statistics
- View other users' public profiles
- Update profile information (name, phone, address, profile image)

## API Endpoints

| Method | Endpoint                              | Description                         | Auth Required |
| ------ | ------------------------------------- | ----------------------------------- | ------------- |
| GET    | `/api/v1/accounts/profile/mine/`      | Get authenticated user's profile    | Yes           |
| GET    | `/api/v1/accounts/profile/<user_id>/` | Get another user's profile          | Yes           |
| PUT    | `/api/v1/accounts/update-profile/`    | Update authenticated user's profile | Yes           |

## Response Format

All responses follow the SER (Success, Error, Response) format:

```json
{
    "success": true,
    "response": { ... },
    "error": null
}
```

### Profile Response Structure

```json
{
	"success": true,
	"response": {
		"user": {
			"id": 1,
			"email": "user@example.com",
			"full_name": "John Doe",
			"phone_number": "+1234567890",
			"address": "123 Main Street",
			"profile_image": "http://example.com/media/profile_images/user_1.jpg",
			"is_staff": false,
			"is_admin": false,
			"date_joined": "2025-01-01T00:00:00Z",
			"issues_reported": 5,
			"progress_updates": 3,
			"issues": [
				{
					"id": 1,
					"title": "Pothole on Main St.",
					"location": "Main St. near 1st Ave.",
					"status": "open",
					"created_at": "2025-01-01T00:00:00Z",
					"category": {
						"id": 1,
						"name": "Potholes"
					}
				}
			]
		}
	},
	"error": null
}
```

## Usage Examples

### Get My Profile

```bash
GET /api/v1/accounts/profile/mine/
Authorization: Bearer <access_token>
```

### Get Another User's Profile

```bash
GET /api/v1/accounts/profile/123/
Authorization: Bearer <access_token>
```

### Update Profile

```bash
PUT /api/v1/accounts/update-profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "full_name": "New Name",
    "phone_number": "+9876543210",
    "address": "456 New Street"
}
```

### Update Profile Image

```bash
PUT /api/v1/accounts/update-profile/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

profile_image: <file>
```

## Test Cases

Run tests with:

```bash
uv run pytest profile/tests.py -v
```

The test suite covers:

- Get my profile with statistics
- Get another user's profile
- Profile not found (404)
- Update profile (full and partial)
- Authentication enforcement
