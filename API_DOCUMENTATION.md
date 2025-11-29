# TownSpark API Documentation

> Complete API Reference for Frontend Integration

**Base URL:** `http://localhost:8000/api/v1`  
**API Version:** v1  
**Authentication:** JWT (Bearer Token)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
    - [Auth](#auth-endpoints)
    - [Users](#user-endpoints)
    - [Issues](#issue-endpoints)
    - [Comments](#comment-endpoints)
    - [Notifications](#notification-endpoints)
    - [Core (Categories, Departments)](#core-endpoints)
    - [Resolver](#resolver-endpoints)
    - [Admin](#admin-endpoints)
6. [Models & Types](#models--types)
7. [Pagination](#pagination)
8. [Filtering & Sorting](#filtering--sorting)
9. [File Uploads](#file-uploads)

---

## Getting Started

### Installation & Setup

```bash
# Clone and install dependencies
cd townspark_backend
uv sync

# Run migrations
uv run python manage.py migrate

# Seed initial data (categories, departments, badges)
uv run python manage.py seed_data

# Start the server
uv run python manage.py runserver 8000
```

### Making API Requests

All API requests should include appropriate headers:

```javascript
// Standard request headers
const headers = {
	"Content-Type": "application/json",
	Accept: "application/json",
};

// For authenticated requests, add:
headers["Authorization"] = `Bearer ${accessToken}`;
```

---

## Authentication

The API uses **JWT (JSON Web Tokens)** for authentication. Tokens are obtained via login and must be included in the `Authorization` header for protected endpoints.

### Token Lifecycle

| Token Type    | Lifetime | Purpose                  |
| ------------- | -------- | ------------------------ |
| Access Token  | 1 day    | API authentication       |
| Refresh Token | 7 days   | Obtain new access tokens |

### How to Use Tokens

```javascript
// Include in request headers
fetch("/api/v1/users/me/", {
	headers: {
		Authorization: "Bearer <access_token>",
	},
});
```

### Token Refresh Flow

1. When access token expires (HTTP 401), use refresh token to get new access token
2. If refresh token is also expired, redirect user to login

---

## Response Format

### Success Response

All successful responses follow this structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Paginated Response

```json
{
  "success": true,
  "message": "Items retrieved successfully",
  "data": {
    "count": 100,
    "next": "http://localhost:8000/api/v1/issues/?page=2",
    "previous": null,
    "results": [ ... ]
  }
}
```

### Error Response

```json
{
	"success": false,
	"error": {
		"code": "ERROR_CODE",
		"message": "Human-readable error message",
		"details": {
			"field_name": ["Specific error for this field"]
		}
	}
}
```

---

## Error Handling

### HTTP Status Codes

| Status | Meaning      | When It Occurs                          |
| ------ | ------------ | --------------------------------------- |
| 200    | OK           | Successful GET, PATCH, DELETE           |
| 201    | Created      | Successful POST (resource created)      |
| 400    | Bad Request  | Validation errors, invalid data         |
| 401    | Unauthorized | Missing or invalid token                |
| 403    | Forbidden    | Insufficient permissions                |
| 404    | Not Found    | Resource doesn't exist                  |
| 409    | Conflict     | Duplicate entry (e.g., already upvoted) |
| 500    | Server Error | Internal server error                   |

### Common Error Codes

| Error Code                | Description                   | Resolution                                |
| ------------------------- | ----------------------------- | ----------------------------------------- |
| `VALIDATION_ERROR`        | Invalid input data            | Check `details` for field-specific errors |
| `AUTHENTICATION_REQUIRED` | No token provided             | Include Bearer token in header            |
| `TOKEN_EXPIRED`           | Access token expired          | Refresh token or re-login                 |
| `PERMISSION_DENIED`       | Not authorized                | Check user role/permissions               |
| `NOT_FOUND`               | Resource doesn't exist        | Verify ID/endpoint                        |
| `ALREADY_ASSIGNED`        | Issue already has resolver    | Cannot reassign                           |
| `DUPLICATE_ENTRY`         | Already exists (upvote, etc.) | Toggle action instead                     |

### Error Handling Example

```javascript
async function apiRequest(url, options) {
	try {
		const response = await fetch(url, options);
		const data = await response.json();

		if (!response.ok) {
			switch (response.status) {
				case 401:
					// Token expired - try refresh
					const newToken = await refreshToken();
					if (newToken) {
						options.headers["Authorization"] = `Bearer ${newToken}`;
						return apiRequest(url, options);
					}
					// Redirect to login
					window.location.href = "/login";
					break;
				case 403:
					alert("You do not have permission for this action");
					break;
				case 400:
					// Show field-specific errors
					Object.entries(data.error.details || {}).forEach(
						([field, errors]) => {
							console.error(`${field}: ${errors.join(", ")}`);
						}
					);
					break;
				default:
					alert(data.error?.message || "An error occurred");
			}
			throw new Error(data.error?.message);
		}

		return data;
	} catch (error) {
		console.error("API Error:", error);
		throw error;
	}
}
```

---

## Endpoints

### Auth Endpoints

#### POST `/auth/login/`

Login with email and password.

**Request:**

```json
{
	"email": "user@example.com",
	"password": "securepassword123"
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "Login successful",
	"data": {
		"tokens": {
			"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
			"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
		},
		"user": {
			"id": 1,
			"name": "John Doe",
			"email": "user@example.com",
			"role": "citizen",
			"profile_image": "http://localhost:8000/media/avatars/1.jpg"
		}
	}
}
```

**Error Responses:**

| Error            | Status | Response                                                                                                                                             |
| ---------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Email not found  | 400    | `{"error": {"message": "Email does not exist", "details": {"email": "No account found with the provided email"}}}`                                   |
| Wrong password   | 400    | `{"error": {"message": "Invalid password", "details": {"password": "The provided password is incorrect for given email."}}}`                         |
| Account inactive | 400    | `{"error": {"message": "Account is inactive", "details": {"email": "The account associated with this email is inactive. Please contact support."}}}` |

---

#### POST `/auth/token/refresh/`

Refresh access token using refresh token.

**Request:**

```json
{
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (401):**

```json
{
	"detail": "Token is invalid or expired",
	"code": "token_not_valid"
}
```

---

#### POST `/auth/users/` (Register)

Register a new citizen account.

**Request:**

```json
{
	"email": "newuser@example.com",
	"password": "SecurePass123!",
	"full_name": "Jane Smith",
	"phone_number": "+977-9812345678",
	"address": "Kathmandu, Nepal"
}
```

**Success Response (201):**

```json
{
	"id": 2,
	"email": "newuser@example.com",
	"full_name": "Jane Smith"
}
```

**Error Responses:**

| Error           | Field     | Message                                |
| --------------- | --------- | -------------------------------------- |
| Duplicate email | email     | "user with this email already exists." |
| Weak password   | password  | "This password is too common."         |
| Missing field   | full_name | "This field is required."              |

---

#### POST `/auth/register/resolver/`

Register as a resolver (requires verification).

**Request:**

```json
{
	"name": "Ram Kumar",
	"email": "resolver@municipality.gov.np",
	"phone": "+977-9801234567",
	"password": "SecurePass123!",
	"confirm_password": "SecurePass123!",
	"department": "1",
	"employee_id": "EMP-001",
	"designation": "Ward Officer"
}
```

**Success Response (201):**

```json
{
	"success": true,
	"message": "Registration successful. Your account is pending verification.",
	"data": {
		"user": {
			"id": 3,
			"name": "Ram Kumar",
			"email": "resolver@municipality.gov.np",
			"role": "resolver"
		},
		"verification_status": "pending"
	}
}
```

---

#### POST `/auth/users/reset_password/`

Request password reset email.

**Request:**

```json
{
	"email": "user@example.com"
}
```

**Success Response (204):** No content

---

### User Endpoints

#### GET `/users/me/`

Get current authenticated user's profile.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "User profile retrieved successfully",
	"data": {
		"id": 1,
		"email": "user@example.com",
		"full_name": "John Doe",
		"name": "John Doe",
		"phone_number": "+977-9812345678",
		"phone": "+977-9812345678",
		"address": "Kathmandu, Nepal",
		"ward": "Ward 10",
		"bio": "Active citizen",
		"location": "Kathmandu",
		"profile_image": "http://localhost:8000/media/avatars/1.jpg",
		"avatar": "http://localhost:8000/media/avatars/1.jpg",
		"role": "citizen",
		"is_active": true,
		"joined_at": "2024-01-15T10:30:00Z",
		"stats": {
			"issues_reported": 12,
			"issues_resolved": 8,
			"upvotes_given": 45,
			"comments_made": 23
		},
		"badges": [
			{
				"id": 1,
				"name": "First Reporter",
				"icon": "🏆",
				"earned_at": "2024-01-16T00:00:00Z"
			}
		]
	}
}
```

---

#### PATCH `/users/me/`

Update current user's profile.

**Headers:** `Authorization: Bearer <token>` (Required)

**Request:** (All fields optional)

```json
{
	"full_name": "John Updated",
	"phone_number": "+977-9812345679",
	"address": "Lalitpur, Nepal",
	"ward": "Ward 5",
	"bio": "Passionate about community",
	"location": "Lalitpur"
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "Profile updated successfully",
	"data": {
		/* Updated user object */
	}
}
```

---

#### GET `/users/me/issues/`

Get issues reported by current user.

**Headers:** `Authorization: Bearer <token>` (Required)

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status: `reported`, `acknowledged`, `in-progress`, `resolved` |

**Success Response (200):**

```json
{
	"success": true,
	"message": "User issues retrieved successfully",
	"data": {
		"results": [
			/* Array of IssueList objects */
		],
		"count": 12
	}
}
```

---

#### GET `/users/me/bookmarks/`

Get issues bookmarked by current user.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Bookmarked issues retrieved successfully",
	"data": {
		"results": [
			/* Array of IssueList objects */
		],
		"count": 5
	}
}
```

---

#### GET `/users/me/upvoted/`

Get issues upvoted by current user.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Upvoted issues retrieved successfully",
	"data": {
		"results": [
			/* Array of IssueList objects */
		],
		"count": 23
	}
}
```

---

#### GET `/users/me/settings/`

Get user settings.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Settings retrieved successfully",
	"data": {
		"notifications": {
			"email": true,
			"push": true,
			"status_updates": true,
			"comments": true,
			"mentions": true
		},
		"privacy": {
			"profile_visible": true,
			"show_email": false
		},
		"preferences": {
			"dark_mode": false,
			"language": "en"
		}
	}
}
```

---

#### PATCH `/users/me/settings/`

Update user settings.

**Headers:** `Authorization: Bearer <token>` (Required)

**Request:**

```json
{
	"notifications": {
		"email": false
	},
	"preferences": {
		"dark_mode": true
	}
}
```

---

#### GET `/users/{id}/`

Get public profile of a user.

**Success Response (200):**

```json
{
	"success": true,
	"message": "User profile retrieved successfully",
	"data": {
		/* User object */
	}
}
```

---

### Issue Endpoints

#### GET `/issues/`

List all issues with filtering and sorting.

**Query Parameters:**

| Parameter | Type   | Description                    | Example                                             |
| --------- | ------ | ------------------------------ | --------------------------------------------------- |
| status    | string | Comma-separated statuses       | `reported,acknowledged`                             |
| category  | string | Comma-separated category IDs   | `1,2,3`                                             |
| urgency   | string | Comma-separated urgency levels | `high,critical`                                     |
| area      | string | Filter by area (partial match) | `Kathmandu`                                         |
| sort      | string | Sort order                     | `newest`, `oldest`, `most_upvotes`, `most_comments` |
| search    | string | Search in title, description   | `pothole`                                           |
| page      | int    | Page number                    | `1`                                                 |

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issues retrieved successfully",
	"data": {
		"count": 156,
		"next": "http://localhost:8000/api/v1/issues/?page=2",
		"previous": null,
		"results": [
			{
				"id": "TS-1042",
				"title": "Broken street light near bus stop",
				"description": "The street light has been non-functional for 2 weeks...",
				"category": "1",
				"status": "reported",
				"urgency": "normal",
				"location": "Main Road, Kathmandu",
				"images": [
					"http://localhost:8000/media/issue_images/TS-1042/abc.jpg"
				],
				"author": {
					"id": 1,
					"name": "John Doe",
					"avatar": null,
					"is_resolver": false,
					"is_admin": false
				},
				"upvotes": 23,
				"uplifts": 23,
				"comments": 5,
				"is_upvoted": false,
				"is_bookmarked": false,
				"created_at": "2024-11-25T10:30:00Z"
			}
		]
	}
}
```

---

#### GET `/issues/{id}/`

Get detailed information about a specific issue.

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issue retrieved successfully",
	"data": {
		"id": "TS-1042",
		"title": "Broken street light near bus stop",
		"description": "Full description of the issue...",
		"category": "1",
		"status": "in-progress",
		"urgency": "high",
		"location": {
			"address": "Main Road, Near City Mall",
			"area": "Kathmandu",
			"coordinates": {
				"lat": 27.7172,
				"lng": 85.324
			}
		},
		"images": [
			"http://localhost:8000/media/issue_images/TS-1042/img1.jpg",
			"http://localhost:8000/media/issue_images/TS-1042/img2.jpg"
		],
		"after_images": [],
		"author": {
			"id": 1,
			"name": "John Doe",
			"avatar": null,
			"is_resolver": false,
			"is_admin": false
		},
		"reporter": {
			/* Same as author */
		},
		"assigned_resolver": {
			"id": 5,
			"name": "Ram Kumar",
			"avatar": null,
			"is_resolver": true,
			"is_admin": false
		},
		"department": {
			"id": 1,
			"name": "Public Works",
			"description": "Handles infrastructure issues",
			"icon": "🔧"
		},
		"upvotes": 45,
		"uplifts": 45,
		"comments": 12,
		"shares": 3,
		"is_upvoted": true,
		"is_bookmarked": false,
		"is_anonymous": false,
		"created_at": "2024-11-20T10:30:00Z",
		"updated_at": "2024-11-25T14:00:00Z",
		"resolved_at": null,
		"timeline": [
			{
				"status": "reported",
				"date": "2024-11-20T10:30:00Z",
				"note": "Issue reported",
				"updated_by": {
					"id": 1,
					"name": "John Doe"
				}
			},
			{
				"status": "acknowledged",
				"date": "2024-11-21T09:00:00Z",
				"note": "Issue accepted by Ram Kumar",
				"updated_by": {
					"id": 5,
					"name": "Ram Kumar"
				}
			},
			{
				"status": "in-progress",
				"date": "2024-11-22T10:00:00Z",
				"note": "Work started on fixing the street light",
				"updated_by": {
					"id": 5,
					"name": "Ram Kumar"
				}
			}
		],
		"official_response": {
			"department": "Public Works",
			"message": "We have dispatched a team to fix the street light. Expected completion: 2 days.",
			"date": "2024-11-22T10:30:00Z",
			"responder": {
				"id": 5,
				"name": "Ram Kumar"
			}
		}
	}
}
```

---

#### POST `/issues/`

Create a new issue.

**Headers:** `Authorization: Bearer <token>` (Required)

**Request (multipart/form-data for images):**

```json
{
  "title": "Pothole on Ring Road",
  "description": "Large pothole causing accidents near the junction",
  "category": 2,
  "urgency": "high",
  "address": "Ring Road, Near Balkhu Bridge",
  "area": "Kathmandu",
  "latitude": 27.6845,
  "longitude": 85.2980,
  "department": 1,
  "is_anonymous": false,
  "images": [File, File]
}
```

**Field Validations:**

| Field        | Required | Validation                                              |
| ------------ | -------- | ------------------------------------------------------- |
| title        | Yes      | Max 200 characters                                      |
| description  | Yes      | Text                                                    |
| category     | Yes      | Valid category ID                                       |
| urgency      | No       | `low`, `normal`, `high`, `critical` (default: `normal`) |
| address      | Yes      | Text                                                    |
| area         | Yes      | Max 100 characters                                      |
| latitude     | No       | Decimal (max 9 digits, 6 decimal places)                |
| longitude    | No       | Decimal (max 9 digits, 6 decimal places)                |
| is_anonymous | No       | Boolean (default: false)                                |
| images       | No       | Max 5 images                                            |

**Success Response (201):**

```json
{
	"success": true,
	"message": "Issue reported successfully",
	"data": {
		/* Full IssueDetail object */
	}
}
```

**Error Response (400):**

```json
{
	"success": false,
	"error": {
		"code": "VALIDATION_ERROR",
		"message": "Validation failed",
		"details": {
			"title": ["This field is required."],
			"category": ["Invalid pk \"99\" - object does not exist."]
		}
	}
}
```

---

#### PATCH `/issues/{id}/`

Update an issue (owner only).

**Headers:** `Authorization: Bearer <token>` (Required)

**Request:**

```json
{
	"title": "Updated title",
	"description": "Updated description",
	"urgency": "critical"
}
```

**Error Response (403):**

```json
{
	"success": false,
	"error": {
		"code": "PERMISSION_DENIED",
		"message": "You do not have permission to perform this action."
	}
}
```

---

#### DELETE `/issues/{id}/`

Delete an issue (owner only).

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issue deleted successfully"
}
```

---

#### POST `/issues/{id}/upvote/`

Toggle upvote on an issue.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issue upvoted",
	"data": {
		"upvoted": true,
		"upvotes": 46
	}
}
```

**Or if removing upvote:**

```json
{
	"success": true,
	"message": "Upvote removed",
	"data": {
		"upvoted": false,
		"upvotes": 45
	}
}
```

---

#### POST `/issues/{id}/bookmark/`

Toggle bookmark on an issue.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issue bookmarked",
	"data": {
		"bookmarked": true
	}
}
```

---

#### POST `/issues/{id}/share/`

Track share action.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Share tracked",
	"data": {
		"shares": 4
	}
}
```

---

#### PATCH `/issues/{id}/status/`

Update issue status (resolver/admin only).

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Resolver or Admin

**Request:**

```json
{
	"status": "in-progress",
	"note": "Work has started on this issue"
}
```

**Valid Status Values:**

- `reported` - Initial status
- `acknowledged` - Issue accepted by resolver
- `in-progress` - Work in progress
- `resolved` - Issue resolved

**Success Response (200):**

```json
{
	"success": true,
	"message": "Status updated successfully",
	"data": {
		/* Updated IssueDetail object */
	}
}
```

---

#### POST `/issues/{id}/assign/`

Assign issue to a resolver (admin only).

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Request:**

```json
{
	"resolver_id": 5
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issue assigned successfully",
	"data": {
		"assigned_to": "Ram Kumar"
	}
}
```

**Error Response (404):**

```json
{
	"success": false,
	"error": {
		"code": "NOT_FOUND",
		"message": "Resolver not found"
	}
}
```

---

#### POST `/issues/{id}/official-response/`

Add official response (resolver/admin only, one per issue).

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Resolver or Admin

**Request:**

```json
{
	"message": "We have dispatched a team to address this issue. Expected resolution within 48 hours."
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "Official response added successfully",
	"data": {
		/* Updated IssueDetail object */
	}
}
```

**Error Response (409):**

```json
{
	"success": false,
	"error": {
		"code": "DUPLICATE_ENTRY",
		"message": "Official response already exists"
	}
}
```

---

### Comment Endpoints

#### GET `/issues/{issue_id}/comments/`

Get comments for an issue.

**Success Response (200):**

```json
{
	"success": true,
	"message": "Comments retrieved successfully",
	"data": {
		"results": [
			{
				"id": "550e8400-e29b-41d4-a716-446655440000",
				"author": {
					"id": 1,
					"name": "John Doe",
					"avatar": null,
					"is_resolver": false,
					"is_admin": false
				},
				"content": "This has been a problem for months!",
				"likes": 5,
				"is_liked": false,
				"created_at": "2024-11-22T11:00:00Z",
				"replies": [
					{
						"id": "550e8400-e29b-41d4-a716-446655440001",
						"author": {
							"id": 2,
							"name": "Jane Smith"
						},
						"content": "I agree, something needs to be done",
						"likes": 2,
						"created_at": "2024-11-22T11:30:00Z"
					}
				]
			}
		],
		"count": 12
	}
}
```

---

#### POST `/issues/{issue_id}/comments/`

Add a comment to an issue.

**Headers:** `Authorization: Bearer <token>` (Required)

**Request:**

```json
{
	"content": "This is my comment on the issue",
	"parent_id": null
}
```

**For replies (nested comment):**

```json
{
	"content": "This is a reply to another comment",
	"parent_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (201):**

```json
{
	"success": true,
	"message": "Comment added successfully",
	"data": {
		"id": "550e8400-e29b-41d4-a716-446655440002",
		"author": {
			/* User object */
		},
		"content": "This is my comment on the issue",
		"likes": 0,
		"is_liked": false,
		"created_at": "2024-11-28T10:00:00Z",
		"replies": []
	}
}
```

---

#### DELETE `/issues/{issue_id}/comments/{comment_id}/`

Delete a comment (owner or admin only).

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Comment deleted successfully"
}
```

**Error Response (403):**

```json
{
	"success": false,
	"error": {
		"code": "PERMISSION_DENIED",
		"message": "You do not have permission to delete this comment"
	}
}
```

---

#### POST `/comments/{comment_id}/like/`

Toggle like on a comment.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Comment liked",
	"data": {
		"liked": true,
		"likes": 6
	}
}
```

---

### Notification Endpoints

#### GET `/notifications/`

Get user's notifications.

**Headers:** `Authorization: Bearer <token>` (Required)

**Query Parameters:**

| Parameter | Type    | Description                                                                                        |
| --------- | ------- | -------------------------------------------------------------------------------------------------- |
| read      | boolean | Filter by read status: `true` or `false`                                                           |
| type      | string  | Filter by type: `issue_update`, `comment`, `upvote`, `badge_earned`, `official_response`, `system` |
| page      | int     | Page number                                                                                        |

**Success Response (200):**

```json
{
	"success": true,
	"message": "Notifications retrieved successfully",
	"data": {
		"results": [
			{
				"id": 1,
				"type": "issue_update",
				"title": "Issue Status Updated",
				"message": "Your issue \"Broken street light\" is now in-progress",
				"read": false,
				"issue": {
					"id": "TS-1042",
					"title": "Broken street light near bus stop"
				},
				"actor": {
					"id": 5,
					"name": "Ram Kumar"
				},
				"created_at": "2024-11-25T10:30:00Z"
			},
			{
				"id": 2,
				"type": "upvote",
				"title": "New Upvote",
				"message": "Someone upvoted your issue",
				"read": true,
				"issue": {
					"id": "TS-1042",
					"title": "Broken street light near bus stop"
				},
				"actor": {
					"id": 3,
					"name": "Jane Smith"
				},
				"created_at": "2024-11-24T15:00:00Z"
			}
		],
		"count": 15,
		"unread_count": 3
	}
}
```

---

#### PATCH `/notifications/{id}/read/`

Mark a notification as read.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Notification marked as read",
	"data": {
		/* Notification object with read: true */
	}
}
```

---

#### POST `/notifications/read-all/`

Mark all notifications as read.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "5 notifications marked as read",
	"data": {
		"marked_count": 5
	}
}
```

---

#### DELETE `/notifications/{id}/`

Delete a notification.

**Headers:** `Authorization: Bearer <token>` (Required)

**Success Response (200):**

```json
{
	"success": true,
	"message": "Notification deleted successfully"
}
```

---

### Core Endpoints

#### GET `/categories/`

List all issue categories.

**Success Response (200):**

```json
{
	"success": true,
	"message": "Categories retrieved successfully",
	"data": [
		{
			"id": 1,
			"name": "Roads & Infrastructure",
			"description": "Issues related to roads, bridges, and public infrastructure",
			"icon": "🛣️",
			"is_active": true
		},
		{
			"id": 2,
			"name": "Water & Sanitation",
			"description": "Water supply and drainage issues",
			"icon": "💧",
			"is_active": true
		},
		{
			"id": 3,
			"name": "Electricity",
			"description": "Street lights and electrical issues",
			"icon": "💡",
			"is_active": true
		},
		{
			"id": 4,
			"name": "Waste Management",
			"description": "Garbage collection and disposal",
			"icon": "🗑️",
			"is_active": true
		},
		{
			"id": 5,
			"name": "Public Safety",
			"description": "Safety and security concerns",
			"icon": "🚨",
			"is_active": true
		}
	]
}
```

---

#### GET `/departments/`

List all departments.

**Success Response (200):**

```json
{
	"success": true,
	"message": "Departments retrieved successfully",
	"data": [
		{
			"id": 1,
			"name": "Public Works",
			"description": "Handles infrastructure and construction",
			"icon": "🔧",
			"contact_email": "publicworks@municipality.gov.np"
		},
		{
			"id": 2,
			"name": "Water Supply",
			"description": "Manages water distribution",
			"icon": "💧",
			"contact_email": "water@municipality.gov.np"
		}
	]
}
```

---

#### GET `/status-options/`

Get available issue status options.

**Success Response (200):**

```json
{
	"success": true,
	"data": [
		{ "value": "reported", "label": "Reported" },
		{ "value": "acknowledged", "label": "Acknowledged" },
		{ "value": "in-progress", "label": "In Progress" },
		{ "value": "resolved", "label": "Resolved" }
	]
}
```

---

#### GET `/urgency-levels/`

Get available urgency levels.

**Success Response (200):**

```json
{
	"success": true,
	"data": [
		{ "value": "low", "label": "Low" },
		{ "value": "normal", "label": "Normal" },
		{ "value": "high", "label": "High" },
		{ "value": "critical", "label": "Critical" }
	]
}
```

---

#### GET `/platform/stats/`

Get platform-wide statistics.

**Success Response (200):**

```json
{
	"success": true,
	"data": {
		"total_issues": 1250,
		"resolved_issues": 890,
		"active_users": 5000,
		"active_resolvers": 45
	}
}
```

---

### Resolver Endpoints

> All resolver endpoints require authentication and resolver role.

#### GET `/resolver/dashboard/`

Get resolver dashboard data.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Resolver

**Success Response (200):**

```json
{
	"success": true,
	"message": "Dashboard data retrieved successfully",
	"data": {
		"stats": {
			"pending": 5,
			"in_progress": 3,
			"resolved_this_month": 12,
			"avg_response_time": "4h"
		},
		"assigned_issues": [
			/* Array of IssueList objects */
		],
		"pending_issues": [
			/* Array of IssueList objects */
		]
	}
}
```

**Error Response (403):**

```json
{
	"success": false,
	"error": {
		"code": "PERMISSION_DENIED",
		"message": "Access denied"
	}
}
```

---

#### GET `/resolver/assigned/`

Get issues assigned to current resolver.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Resolver

**Query Parameters:**

| Parameter | Type   | Description       |
| --------- | ------ | ----------------- |
| status    | string | Filter by status  |
| urgency   | string | Filter by urgency |

**Success Response (200):**

```json
{
	"success": true,
	"message": "Assigned issues retrieved successfully",
	"data": {
		"results": [
			/* Array of IssueList objects */
		],
		"count": 8
	}
}
```

---

#### GET `/resolver/pending/`

Get pending issues (not yet assigned).

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Resolver

**Success Response (200):**

```json
{
	"success": true,
	"message": "Pending issues retrieved successfully",
	"data": {
		"results": [
			/* Array of IssueList objects */
		],
		"count": 15
	}
}
```

---

#### POST `/resolver/issues/{id}/accept/`

Accept/claim an issue.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Resolver

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issue accepted successfully",
	"data": {
		"id": "TS-1042",
		"status": "acknowledged"
	}
}
```

**Error Response (400):**

```json
{
	"success": false,
	"error": {
		"code": "ALREADY_ASSIGNED",
		"message": "Issue already assigned"
	}
}
```

---

#### POST `/resolver/issues/{id}/complete/`

Mark an issue as resolved.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Resolver (must be assigned)

**Request (multipart/form-data for images):**

```json
{
  "resolution_note": "Street light has been repaired and is now functional",
  "after_images": [File, File]
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "Issue marked as resolved",
	"data": {
		"id": "TS-1042",
		"status": "resolved"
	}
}
```

---

### Admin Endpoints

> All admin endpoints require authentication and admin role.

#### GET `/admin/dashboard/`

Get admin dashboard data.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Success Response (200):**

```json
{
	"success": true,
	"message": "Admin dashboard data retrieved successfully",
	"data": {
		"stats": {
			"total_users": 5000,
			"active_resolvers": 45,
			"total_issues": 1250,
			"resolved_issues": 890,
			"pending_verification": 3,
			"avg_resolution_time": "48h"
		}
	}
}
```

---

#### GET `/admin/users/`

List all citizen users.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Query Parameters:**

| Parameter | Type   | Description                     |
| --------- | ------ | ------------------------------- |
| search    | string | Search by name or email         |
| status    | string | Filter: `active` or `suspended` |
| page      | int    | Page number                     |

**Success Response (200):**

```json
{
	"success": true,
	"message": "Users retrieved successfully",
	"data": {
		"results": [
			/* Array of User objects */
		],
		"count": 500,
		"stats": {
			"total": 5000,
			"active": 4800,
			"suspended": 200
		}
	}
}
```

---

#### GET `/admin/users/{id}/`

Get specific user details.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

---

#### PATCH `/admin/users/{id}/`

Update user details.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

---

#### DELETE `/admin/users/{id}/`

Delete a user.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Success Response (200):**

```json
{
	"success": true,
	"message": "User deleted successfully"
}
```

---

#### POST `/admin/users/{id}/toggle-status/`

Toggle user active status (activate/deactivate).

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Request:**

```json
{
	"is_active": false
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "User deactivated successfully",
	"data": {
		"id": 25,
		"is_active": false
	}
}
```

---

#### GET `/admin/resolvers/`

List all resolvers.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Success Response (200):**

```json
{
	"success": true,
	"message": "Resolvers retrieved successfully",
	"data": {
		"results": [
			{
				"id": 5,
				"email": "resolver@municipality.gov.np",
				"full_name": "Ram Kumar",
				"role": "resolver",
				"resolver_profile": {
					"designation": "Ward Officer",
					"employee_id": "EMP-001",
					"department": {
						"id": 1,
						"name": "Public Works"
					},
					"is_verified": true,
					"verified_at": "2024-01-20T00:00:00Z",
					"stats": {
						"pending": 2,
						"in_progress": 3,
						"resolved_this_month": 15
					}
				}
			}
		],
		"count": 45,
		"stats": {
			"total": 48,
			"verified": 45,
			"pending": 3
		}
	}
}
```

---

#### GET `/admin/resolvers/pending/`

Get resolvers pending verification.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

---

#### POST `/admin/resolvers/{id}/verify/`

Verify a resolver.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Request:**

```json
{
	"approved": true
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "Resolver verified successfully",
	"data": {
		"id": 10,
		"is_verified": true
	}
}
```

---

#### POST `/admin/resolvers/{id}/reject/`

Reject a resolver verification (deletes user).

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

**Request:**

```json
{
	"reason": "Invalid employee ID provided"
}
```

**Success Response (200):**

```json
{
	"success": true,
	"message": "Resolver rejected and removed"
}
```

---

#### DELETE `/admin/resolvers/{id}/`

Delete a resolver.

**Headers:** `Authorization: Bearer <token>` (Required)  
**Permission:** Admin

---

## Models & Types

### User Object

```typescript
interface User {
	id: number;
	email: string;
	full_name: string;
	name: string;
	phone_number: string | null;
	phone: string | null;
	address: string | null;
	ward: string | null;
	bio: string | null;
	location: string | null;
	profile_image: string | null;
	avatar: string | null;
	role: "citizen" | "resolver" | "admin";
	is_active: boolean;
	joined_at: string; // ISO datetime
	stats: UserStats;
	badges: Badge[];
}

interface UserStats {
	issues_reported: number;
	issues_resolved: number;
	upvotes_given: number;
	comments_made: number;
}

interface Badge {
	id: number;
	name: string;
	icon: string;
	earned_at: string;
}
```

### Issue Objects

```typescript
interface IssueList {
	id: string; // Format: "TS-XXXX"
	title: string;
	description: string;
	category: string;
	status: IssueStatus;
	urgency: UrgencyLevel;
	location: string;
	images: string[];
	author: UserMinimal;
	upvotes: number;
	uplifts: number;
	comments: number;
	is_upvoted: boolean;
	is_bookmarked: boolean;
	created_at: string;
}

interface IssueDetail extends IssueList {
	location: {
		address: string;
		area: string;
		coordinates: {
			lat: number | null;
			lng: number | null;
		};
	};
	after_images: string[];
	reporter: UserMinimal;
	assigned_resolver: UserMinimal | null;
	department: Department | null;
	shares: number;
	is_anonymous: boolean;
	updated_at: string;
	resolved_at: string | null;
	timeline: TimelineEntry[];
	official_response: OfficialResponse | null;
}

type IssueStatus = "reported" | "acknowledged" | "in-progress" | "resolved";
type UrgencyLevel = "low" | "normal" | "high" | "critical";
```

### Other Types

```typescript
interface UserMinimal {
	id: number;
	name: string;
	avatar: string | null;
	is_resolver: boolean;
	is_admin: boolean;
}

interface Category {
	id: number;
	name: string;
	description: string;
	icon: string;
	is_active: boolean;
}

interface Department {
	id: number;
	name: string;
	description: string;
	icon: string;
	contact_email: string;
}

interface TimelineEntry {
	status: IssueStatus;
	date: string;
	note: string;
	updated_by: UserMinimal;
}

interface OfficialResponse {
	department: string;
	message: string;
	date: string;
	responder: UserMinimal;
}

interface Comment {
	id: string; // UUID
	author: UserMinimal;
	content: string;
	likes: number;
	is_liked: boolean;
	created_at: string;
	replies: Comment[];
}

interface Notification {
	id: number;
	type: NotificationType;
	title: string;
	message: string;
	read: boolean;
	issue: { id: string; title: string } | null;
	actor: UserMinimal | null;
	created_at: string;
}

type NotificationType =
	| "issue_update"
	| "comment"
	| "upvote"
	| "badge_earned"
	| "official_response"
	| "system";
```

---

## Pagination

The API uses page-based pagination with a default page size of 20.

### Request

```
GET /api/v1/issues/?page=2
```

### Response

```json
{
  "success": true,
  "data": {
    "count": 156,
    "next": "http://localhost:8000/api/v1/issues/?page=3",
    "previous": "http://localhost:8000/api/v1/issues/?page=1",
    "results": [...]
  }
}
```

### Implementation Example

```javascript
async function fetchIssues(page = 1) {
	const response = await fetch(`/api/v1/issues/?page=${page}`);
	const data = await response.json();

	return {
		issues: data.data.results,
		totalCount: data.data.count,
		hasNext: !!data.data.next,
		hasPrevious: !!data.data.previous,
	};
}
```

---

## Filtering & Sorting

### Issues Filtering

```
GET /api/v1/issues/?status=reported,acknowledged&category=1,2&urgency=high,critical&area=Kathmandu&sort=most_upvotes
```

| Parameter | Description                    | Values                                                |
| --------- | ------------------------------ | ----------------------------------------------------- |
| status    | Filter by status(es)           | `reported`, `acknowledged`, `in-progress`, `resolved` |
| category  | Filter by category ID(s)       | Comma-separated IDs                                   |
| urgency   | Filter by urgency level(s)     | `low`, `normal`, `high`, `critical`                   |
| area      | Filter by area (partial match) | Text                                                  |
| search    | Search in title/description    | Text                                                  |
| sort      | Sort order                     | `newest`, `oldest`, `most_upvotes`, `most_comments`   |

### Implementation Example

```javascript
function buildIssueQuery(filters) {
	const params = new URLSearchParams();

	if (filters.status?.length) {
		params.set("status", filters.status.join(","));
	}
	if (filters.categories?.length) {
		params.set("category", filters.categories.join(","));
	}
	if (filters.urgency?.length) {
		params.set("urgency", filters.urgency.join(","));
	}
	if (filters.area) {
		params.set("area", filters.area);
	}
	if (filters.search) {
		params.set("search", filters.search);
	}
	if (filters.sort) {
		params.set("sort", filters.sort);
	}
	if (filters.page) {
		params.set("page", filters.page);
	}

	return `/api/v1/issues/?${params.toString()}`;
}
```

---

## File Uploads

### Uploading Issue Images

Use `multipart/form-data` for file uploads:

```javascript
async function createIssue(issueData, images) {
	const formData = new FormData();

	// Add text fields
	formData.append("title", issueData.title);
	formData.append("description", issueData.description);
	formData.append("category", issueData.category);
	formData.append("urgency", issueData.urgency);
	formData.append("address", issueData.address);
	formData.append("area", issueData.area);

	if (issueData.latitude) {
		formData.append("latitude", issueData.latitude);
	}
	if (issueData.longitude) {
		formData.append("longitude", issueData.longitude);
	}

	// Add images (max 5)
	images.slice(0, 5).forEach((image, index) => {
		formData.append("images", image);
	});

	const response = await fetch("/api/v1/issues/", {
		method: "POST",
		headers: {
			Authorization: `Bearer ${accessToken}`,
			// Don't set Content-Type - let browser set it with boundary
		},
		body: formData,
	});

	return response.json();
}
```

### Image Constraints

- **Maximum files:** 5 images per issue
- **Supported formats:** JPEG, PNG, GIF, WebP
- **Maximum file size:** Recommended < 5MB each

---

## Quick Reference

### Status Flow

```
reported → acknowledged → in-progress → resolved
```

### Role Permissions

| Endpoint              | Citizen | Resolver | Admin |
| --------------------- | ------- | -------- | ----- |
| View issues           | ✅      | ✅       | ✅    |
| Create issue          | ✅      | ✅       | ✅    |
| Edit own issue        | ✅      | ✅       | ✅    |
| Upvote/Bookmark       | ✅      | ✅       | ✅    |
| Comment               | ✅      | ✅       | ✅    |
| Update issue status   | ❌      | ✅       | ✅    |
| Assign resolver       | ❌      | ❌       | ✅    |
| Accept issue          | ❌      | ✅       | ✅    |
| Add official response | ❌      | ✅       | ✅    |
| Verify resolver       | ❌      | ❌       | ✅    |
| Manage users          | ❌      | ❌       | ✅    |

### Common Headers

```javascript
const headers = {
	"Content-Type": "application/json",
	Accept: "application/json",
	Authorization: "Bearer <access_token>", // For authenticated requests
};
```

---

## Support

For API issues or questions, contact the backend development team.

**Version:** 1.0.0  
**Last Updated:** November 2024
