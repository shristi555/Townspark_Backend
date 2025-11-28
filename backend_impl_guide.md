# TownSpark Backend Implementation Guide

This document provides comprehensive guidelines for backend developers to implement Django REST APIs that seamlessly integrate with the TownSpark React frontend. Following this guide ensures that hardcoded frontend values can be replaced without modifications.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [API Base Configuration](#api-base-configuration)
4. [Data Models](#data-models)
5. [API Endpoints](#api-endpoints)
6. [Response Structures](#response-structures)
7. [Error Handling](#error-handling)
8. [Pagination & Filtering](#pagination--filtering)
9. [File Upload Guidelines](#file-upload-guidelines)
10. [WebSocket Events](#websocket-events)

---

## Overview

### Tech Stack

- **Backend Framework**: Django 4.x + Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL (recommended)
- **File Storage**: Django Storages (S3/Local)
- **Real-time**: Django Channels (for notifications)

### API Versioning

All endpoints should be prefixed with `/api/v1/`

### Base URL Structure

```
https://api.townspark.com/api/v1/
```

---

## Authentication & Authorization

### JWT Configuration

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Auth Endpoints

| Endpoint                               | Method | Description            |
| -------------------------------------- | ------ | ---------------------- |
| `/api/v1/auth/register/`               | POST   | User registration      |
| `/api/v1/auth/register/resolver/`      | POST   | Resolver registration  |
| `/api/v1/auth/login/`                  | POST   | User login             |
| `/api/v1/auth/logout/`                 | POST   | User logout            |
| `/api/v1/auth/token/refresh/`          | POST   | Refresh access token   |
| `/api/v1/auth/password/reset/`         | POST   | Request password reset |
| `/api/v1/auth/password/reset/confirm/` | POST   | Confirm password reset |
| `/api/v1/auth/password/change/`        | POST   | Change password        |

### User Roles

```python
class UserRole(models.TextChoices):
    CITIZEN = 'citizen', 'Citizen'
    RESOLVER = 'resolver', 'Resolver'
    ADMIN = 'admin', 'Admin'
```

---

## API Base Configuration

### Request Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json
```

### Standard Response Format

```json
{
    "success": true,
    "message": "Operation successful",
    "data": { ... },
    "meta": {
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

### Error Response Format

```json
{
	"success": false,
	"message": "Error description",
	"errors": {
		"field_name": ["Error message 1", "Error message 2"]
	},
	"error_code": "VALIDATION_ERROR",
	"meta": {
		"timestamp": "2024-01-15T10:30:00Z"
	}
}
```

---

## Data Models

### User Model

```python
# models.py
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CITIZEN)
    address = models.TextField(blank=True)
    ward = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Stats (can be computed or cached)
    @property
    def stats(self):
        return {
            'issues_posted': self.issues.count(),
            'uplifts_received': self.get_total_uplifts(),
            'issues_resolved': self.issues.filter(status='resolved').count()
        }
```

**JSON Response Structure (User):**

```json
{
	"id": "user-1",
	"name": "Jane Doe",
	"username": "janedoe_spark",
	"email": "jane.doe@email.com",
	"phone": "+1 234 567 8900",
	"avatar": "https://example.com/avatars/user-1.jpg",
	"role": "citizen",
	"address": "123 Main Street, TownSpark",
	"ward": "Ward A",
	"bio": "Community advocate",
	"location": "TownSpark, State",
	"is_active": true,
	"joined_at": "2023-06-15T00:00:00Z",
	"stats": {
		"issues_posted": 12,
		"uplifts_received": 87,
		"issues_resolved": 5
	},
	"badges": ["Community Hero", "First Report", "10 Issues Resolved"]
}
```

### Resolver Model (Extended User)

```python
class ResolverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resolver_profile')
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    designation = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    jurisdiction = models.TextField(help_text="Comma-separated ward names")
    id_document = models.FileField(upload_to='resolver_docs/')
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_resolvers')
```

**JSON Response Structure (Resolver):**

```json
{
	"id": "resolver-1",
	"name": "John Smith",
	"email": "john.smith@publicworks.gov",
	"avatar": "https://example.com/avatars/resolver-1.jpg",
	"role": "resolver",
	"department": {
		"id": "public-works",
		"name": "Public Works",
		"icon": "construction"
	},
	"designation": "Field Officer",
	"employee_id": "EMP-12345",
	"jurisdiction": "Ward A, Ward B",
	"is_verified": true,
	"verified_at": "2023-06-20T10:00:00Z",
	"stats": {
		"pending": 12,
		"in_progress": 5,
		"resolved_this_month": 48,
		"avg_response_time": "2.5 days"
	}
}
```

### Issue Model

```python
class Issue(models.Model):
    class Status(models.TextChoices):
        REPORTED = 'reported', 'Reported'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        IN_PROGRESS = 'in-progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    class Urgency(models.TextChoices):
        LOW = 'low', 'Low'
        NORMAL = 'normal', 'Normal'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    id = models.CharField(max_length=20, primary_key=True)  # Format: TS-XXXX
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    urgency = models.CharField(max_length=20, choices=Urgency.choices, default=Urgency.NORMAL)

    # Location
    address = models.TextField()
    area = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    # Relations
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    assigned_resolver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_issues')
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)

    # Flags
    is_anonymous = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_issue_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_issue_id():
        last_issue = Issue.objects.order_by('-created_at').first()
        if last_issue:
            num = int(last_issue.id.split('-')[1]) + 1
        else:
            num = 1000
        return f"TS-{num}"
```

**JSON Response Structure (Issue - Full):**

```json
{
	"id": "TS-1138",
	"title": "Large Pothole on Main Street",
	"description": "A large pothole near the intersection of Main and 1st...",
	"category": "road",
	"status": "reported",
	"urgency": "high",
	"location": {
		"address": "123 Main Street",
		"area": "Oakwood District",
		"coordinates": {
			"lat": 40.7128,
			"lng": -74.006
		}
	},
	"images": [
		"https://example.com/issues/TS-1138/image1.jpg",
		"https://example.com/issues/TS-1138/image2.jpg"
	],
	"author": {
		"id": "user-2",
		"name": "Alex Chen",
		"avatar": "https://example.com/avatars/user-2.jpg"
	},
	"reporter": {
		"id": "user-2",
		"name": "Alex Chen",
		"avatar": "https://example.com/avatars/user-2.jpg"
	},
	"assigned_resolver": null,
	"department": {
		"id": "public-works",
		"name": "Public Works"
	},
	"upvotes": 128,
	"uplifts": 128,
	"comments": 16,
	"shares": 8,
	"is_upvoted": false,
	"is_bookmarked": false,
	"is_anonymous": false,
	"created_at": "2023-10-26T10:30:00Z",
	"updated_at": "2023-10-27T09:00:00Z",
	"timeline": [
		{
			"status": "reported",
			"date": "2023-10-26T10:30:00Z",
			"note": "Issue reported",
			"updated_by": null
		}
	],
	"official_response": null,
	"after_images": []
}
```

**JSON Response Structure (Issue - Compact/List):**

```json
{
	"id": "TS-1138",
	"title": "Large Pothole on Main Street",
	"description": "A large pothole near the intersection...",
	"category": "road",
	"status": "reported",
	"urgency": "high",
	"location": "123 Main Street, Oakwood District",
	"images": ["https://example.com/issues/TS-1138/image1.jpg"],
	"author": {
		"id": "user-2",
		"name": "Alex Chen",
		"avatar": "https://example.com/avatars/user-2.jpg"
	},
	"upvotes": 128,
	"comments": 16,
	"created_at": "2023-10-26T10:30:00Z"
}
```

### Issue Image Model

```python
class IssueImage(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='issue_images')
    image = models.ImageField(upload_to='issue_images/')
    is_after_image = models.BooleanField(default=False)  # For resolved issue comparison
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### Issue Timeline Model

```python
class IssueTimeline(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='timeline_entries')
    status = models.CharField(max_length=20, choices=Issue.Status.choices)
    note = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Official Response Model

```python
class OfficialResponse(models.Model):
    issue = models.OneToOneField(Issue, on_delete=models.CASCADE, related_name='official_response_obj')
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**JSON Response Structure (Official Response):**

```json
{
	"department": "Public Works Dept.",
	"message": "Thank you for reporting. A crew has been dispatched...",
	"date": "2023-10-26T11:00:00Z",
	"responder": {
		"id": "resolver-1",
		"name": "John Smith"
	}
}
```

### Category Model

```python
class Category(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)  # Material icon name
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
```

**JSON Response Structure (Category):**

```json
{
	"id": "road",
	"name": "Road Maintenance",
	"icon": "car_repair",
	"description": "Issues related to roads, potholes, etc."
}
```

### Department Model

```python
class Department(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
```

**JSON Response Structure (Department):**

```json
{
	"id": "public-works",
	"name": "Public Works",
	"icon": "construction",
	"description": "Handles infrastructure and public utilities"
}
```

### Comment Model

```python
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='issue_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**JSON Response Structure (Comment):**

```json
{
    "id": "comment-1",
    "issue_id": "TS-1138",
    "author": {
        "id": "user-5",
        "name": "John D.",
        "avatar": "https://example.com/avatars/user-5.jpg",
        "is_resolver": false,
        "is_admin": false
    },
    "content": "Thanks for the update! This one was getting pretty bad.",
    "likes": 5,
    "created_at": "2023-10-27T11:00:00Z",
    "replies": [
        {
            "id": "reply-1",
            "author": {...},
            "content": "I agree!",
            "likes": 2,
            "created_at": "2023-10-27T12:00:00Z"
        }
    ]
}
```

### Notification Model

```python
class Notification(models.Model):
    class NotificationType(models.TextChoices):
        STATUS_UPDATE = 'status_update', 'Status Update'
        COMMENT = 'comment', 'New Comment'
        UPVOTE = 'upvote', 'Upvote'
        MENTION = 'mention', 'Mention'
        RESOLUTION = 'resolution', 'Resolution'
        ASSIGNMENT = 'assignment', 'Assignment'
        SYSTEM = 'system', 'System'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True, blank=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='triggered_notifications')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**JSON Response Structure (Notification):**

```json
{
	"id": "notif-1",
	"type": "status_update",
	"title": "Status Update",
	"message": "Your issue 'Large Pothole on Main Street' has been acknowledged by Public Works.",
	"issue": {
		"id": "TS-1138",
		"title": "Large Pothole on Main Street"
	},
	"actor": {
		"id": "resolver-1",
		"name": "John Smith",
		"avatar": "https://example.com/avatars/resolver-1.jpg"
	},
	"read": false,
	"created_at": "2024-01-15T10:30:00Z"
}
```

### Upvote Model

```python
class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='upvote_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'issue']
```

### Bookmark Model

```python
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='bookmark_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'issue']
```

### Badge Model

```python
class Badge(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    criteria = models.JSONField()  # Criteria for earning the badge

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
```

---

## API Endpoints

### Authentication Endpoints

#### POST `/api/v1/auth/register/`

**Request:**

```json
{
	"name": "Jane Doe",
	"email": "jane.doe@email.com",
	"phone": "1234567890",
	"password": "securepassword123",
	"confirm_password": "securepassword123",
	"user_type": "citizen"
}
```

**Response (201 Created):**

```json
{
	"success": true,
	"message": "Registration successful. Please verify your email.",
	"data": {
		"user": {
			"id": "user-123",
			"name": "Jane Doe",
			"email": "jane.doe@email.com",
			"role": "citizen"
		},
		"tokens": {
			"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
			"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
		}
	}
}
```

#### POST `/api/v1/auth/register/resolver/`

**Request:**

```json
{
	"name": "John Smith",
	"email": "john.smith@publicworks.gov",
	"phone": "1234567890",
	"password": "securepassword123",
	"confirm_password": "securepassword123",
	"department": "public-works",
	"employee_id": "EMP-12345",
	"designation": "Field Officer",
	"id_document": "<file>"
}
```

**Response (201 Created):**

```json
{
	"success": true,
	"message": "Registration successful. Your account is pending verification.",
	"data": {
		"user": {
			"id": "resolver-123",
			"name": "John Smith",
			"email": "john.smith@publicworks.gov",
			"role": "resolver"
		},
		"verification_status": "pending"
	}
}
```

#### POST `/api/v1/auth/login/`

**Request:**

```json
{
	"email": "jane.doe@email.com",
	"password": "securepassword123"
}
```

**Response (200 OK):**

```json
{
	"success": true,
	"message": "Login successful",
	"data": {
		"user": {
			"id": "user-1",
			"name": "Jane Doe",
			"username": "janedoe_spark",
			"email": "jane.doe@email.com",
			"phone": "+1 234 567 8900",
			"avatar": "https://example.com/avatars/user-1.jpg",
			"role": "citizen",
			"address": "123 Main Street, TownSpark",
			"ward": "Ward A",
			"joined_at": "2023-06-15T00:00:00Z",
			"stats": {
				"issues_posted": 12,
				"uplifts_received": 87,
				"issues_resolved": 5
			},
			"badges": ["Community Hero", "First Report"]
		},
		"tokens": {
			"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
			"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
		}
	}
}
```

#### POST `/api/v1/auth/token/refresh/`

**Request:**

```json
{
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
		"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
	}
}
```

---

### User Endpoints

#### GET `/api/v1/users/me/`

Get current authenticated user profile.

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"id": "user-1",
		"name": "Jane Doe",
		"username": "janedoe_spark",
		"email": "jane.doe@email.com",
		"phone": "+1 234 567 8900",
		"avatar": "https://example.com/avatars/user-1.jpg",
		"role": "citizen",
		"address": "123 Main Street, TownSpark",
		"ward": "Ward A",
		"bio": "Community advocate",
		"location": "TownSpark, State",
		"is_active": true,
		"joined_at": "2023-06-15T00:00:00Z",
		"stats": {
			"issues_posted": 12,
			"uplifts_received": 87,
			"issues_resolved": 5
		},
		"badges": ["Community Hero", "First Report", "10 Issues Resolved"]
	}
}
```

#### PATCH `/api/v1/users/me/`

Update current user profile.

**Request:**

```json
{
	"name": "Jane Doe Updated",
	"phone": "+1 234 567 8901",
	"bio": "Updated bio",
	"address": "456 New Street"
}
```

#### GET `/api/v1/users/{id}/`

Get user by ID (public profile).

#### GET `/api/v1/users/me/issues/`

Get current user's issues.

**Query Parameters:**

- `status`: Filter by status (reported, acknowledged, in-progress, resolved)
- `page`: Page number
- `page_size`: Items per page (default: 10)

**Response (200 OK):**

```json
{
    "success": true,
    "data": {
        "results": [...],
        "count": 12,
        "next": "/api/v1/users/me/issues/?page=2",
        "previous": null
    }
}
```

#### GET `/api/v1/users/me/bookmarks/`

Get current user's bookmarked issues.

#### GET `/api/v1/users/me/upvoted/`

Get issues upvoted by current user.

---

### Issue Endpoints

#### GET `/api/v1/issues/`

List all issues (feed).

**Query Parameters:**

- `status`: Filter by status
- `category`: Filter by category ID
- `urgency`: Filter by urgency
- `area`: Filter by area
- `search`: Search in title and description
- `sort`: Sort order (newest, oldest, most_upvotes, most_comments)
- `lat` & `lng` & `radius`: Filter by location proximity
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"results": [
			{
				"id": "TS-1138",
				"title": "Large Pothole on Main Street",
				"description": "A large pothole near...",
				"category": "road",
				"status": "reported",
				"urgency": "high",
				"location": "123 Main Street, Oakwood District",
				"images": ["https://example.com/issues/TS-1138/image1.jpg"],
				"author": {
					"id": "user-2",
					"name": "Alex Chen",
					"avatar": "https://example.com/avatars/user-2.jpg"
				},
				"upvotes": 128,
				"comments": 16,
				"created_at": "2023-10-26T10:30:00Z"
			}
		],
		"count": 100,
		"next": "/api/v1/issues/?page=2",
		"previous": null
	}
}
```

#### POST `/api/v1/issues/`

Create a new issue.

**Request (multipart/form-data):**

```json
{
	"title": "Large Pothole on Main Street",
	"description": "A large pothole near the intersection...",
	"category": "road",
	"urgency": "high",
	"address": "123 Main Street",
	"area": "Oakwood District",
	"latitude": 40.7128,
	"longitude": -74.006,
	"department": "public-works",
	"is_anonymous": false,
	"images": ["<file1>", "<file2>"]
}
```

**Response (201 Created):**

```json
{
    "success": true,
    "message": "Issue reported successfully",
    "data": {
        "id": "TS-1142",
        "title": "Large Pothole on Main Street",
        ...
    }
}
```

#### GET `/api/v1/issues/{id}/`

Get issue details.

**Response (200 OK):**
Returns full issue structure as defined above.

#### PATCH `/api/v1/issues/{id}/`

Update issue (reporter only for basic fields, resolver/admin for status).

#### DELETE `/api/v1/issues/{id}/`

Delete issue (reporter or admin only).

#### POST `/api/v1/issues/{id}/upvote/`

Toggle upvote on issue.

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"upvoted": true,
		"upvotes": 129
	}
}
```

#### POST `/api/v1/issues/{id}/bookmark/`

Toggle bookmark on issue.

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"bookmarked": true
	}
}
```

#### POST `/api/v1/issues/{id}/share/`

Track share action.

#### PATCH `/api/v1/issues/{id}/status/`

Update issue status (resolver/admin only).

**Request:**

```json
{
	"status": "acknowledged",
	"note": "Issue has been reviewed and assigned"
}
```

**Response (200 OK):**

```json
{
    "success": true,
    "message": "Status updated successfully",
    "data": {
        "id": "TS-1138",
        "status": "acknowledged",
        "timeline": [...]
    }
}
```

#### POST `/api/v1/issues/{id}/assign/`

Assign issue to resolver (admin only).

**Request:**

```json
{
	"resolver_id": "resolver-1"
}
```

#### POST `/api/v1/issues/{id}/official-response/`

Add official response (resolver/admin only).

**Request:**

```json
{
	"message": "Thank you for reporting. A crew has been dispatched..."
}
```

---

### Comment Endpoints

#### GET `/api/v1/issues/{issue_id}/comments/`

Get comments for an issue.

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"results": [
			{
				"id": "comment-1",
				"author": {
					"id": "user-5",
					"name": "John D.",
					"avatar": "https://example.com/avatars/user-5.jpg",
					"is_resolver": false,
					"is_admin": false
				},
				"content": "Thanks for the update!",
				"likes": 5,
				"created_at": "2023-10-27T11:00:00Z",
				"replies": []
			}
		],
		"count": 16
	}
}
```

#### POST `/api/v1/issues/{issue_id}/comments/`

Add comment to issue.

**Request:**

```json
{
	"content": "Thanks for the update!",
	"parent_id": null
}
```

#### POST `/api/v1/comments/{id}/like/`

Toggle like on comment.

#### DELETE `/api/v1/comments/{id}/`

Delete comment (author or admin only).

---

### Notification Endpoints

#### GET `/api/v1/notifications/`

Get user's notifications.

**Query Parameters:**

- `read`: Filter by read status (true/false)
- `type`: Filter by notification type

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"results": [
			{
				"id": "notif-1",
				"type": "status_update",
				"title": "Status Update",
				"message": "Your issue 'Large Pothole' has been acknowledged...",
				"issue": {
					"id": "TS-1138",
					"title": "Large Pothole on Main Street"
				},
				"actor": {
					"id": "resolver-1",
					"name": "John Smith",
					"avatar": "https://example.com/avatars/resolver-1.jpg"
				},
				"read": false,
				"created_at": "2024-01-15T10:30:00Z"
			}
		],
		"unread_count": 5,
		"count": 20
	}
}
```

#### PATCH `/api/v1/notifications/{id}/read/`

Mark notification as read.

#### POST `/api/v1/notifications/read-all/`

Mark all notifications as read.

#### DELETE `/api/v1/notifications/{id}/`

Delete notification.

---

### Category & Department Endpoints

#### GET `/api/v1/categories/`

Get all categories.

**Response (200 OK):**

```json
{
	"success": true,
	"data": [
		{ "id": "road", "name": "Road Maintenance", "icon": "car_repair" },
		{ "id": "garbage", "name": "Garbage & Waste", "icon": "delete" },
		{ "id": "sewage", "name": "Sewage & Drains", "icon": "water_drop" },
		{ "id": "electricity", "name": "Electricity", "icon": "bolt" },
		{ "id": "streetlight", "name": "Street Light", "icon": "lightbulb" },
		{ "id": "water", "name": "Water Supply", "icon": "water" },
		{ "id": "traffic", "name": "Traffic", "icon": "traffic" },
		{
			"id": "graffiti",
			"name": "Graffiti & Vandalism",
			"icon": "format_paint"
		},
		{ "id": "parks", "name": "Parks & Gardens", "icon": "park" },
		{ "id": "other", "name": "Other", "icon": "more_horiz" }
	]
}
```

#### GET `/api/v1/departments/`

Get all departments.

**Response (200 OK):**

```json
{
	"success": true,
	"data": [
		{
			"id": "public-works",
			"name": "Public Works",
			"icon": "construction"
		},
		{ "id": "sanitation", "name": "Sanitation", "icon": "delete" },
		{ "id": "traffic", "name": "Traffic Management", "icon": "traffic" },
		{ "id": "parks", "name": "Parks & Recreation", "icon": "park" },
		{ "id": "utilities", "name": "Utilities", "icon": "bolt" },
		{ "id": "housing", "name": "Housing", "icon": "home" },
		{ "id": "environment", "name": "Environment", "icon": "eco" }
	]
}
```

#### GET `/api/v1/status-options/`

Get all status options.

**Response (200 OK):**

```json
{
	"success": true,
	"data": [
		{
			"id": "reported",
			"name": "Reported",
			"color": "status-reported",
			"icon": "report"
		},
		{
			"id": "acknowledged",
			"name": "Acknowledged",
			"color": "status-acknowledged",
			"icon": "verified_user"
		},
		{
			"id": "in-progress",
			"name": "In Progress",
			"color": "status-progress",
			"icon": "hourglass_top"
		},
		{
			"id": "resolved",
			"name": "Resolved",
			"color": "status-resolved",
			"icon": "task_alt"
		}
	]
}
```

#### GET `/api/v1/urgency-levels/`

Get all urgency levels.

**Response (200 OK):**

```json
{
	"success": true,
	"data": [
		{ "id": "low", "name": "Low", "color": "urgency-low" },
		{ "id": "normal", "name": "Normal", "color": "urgency-normal" },
		{ "id": "high", "name": "High", "color": "urgency-high" },
		{ "id": "critical", "name": "Critical", "color": "urgency-critical" }
	]
}
```

---

### Resolver Endpoints

#### GET `/api/v1/resolver/dashboard/`

Get resolver dashboard data.

**Response (200 OK):**

```json
{
    "success": true,
    "data": {
        "stats": {
            "assigned": 12,
            "in_progress": 5,
            "resolved_this_month": 48,
            "avg_response_time": "2.5 days"
        },
        "assigned_issues": [...],
        "pending_issues": [...],
        "recent_activity": [...]
    }
}
```

#### GET `/api/v1/resolver/assigned/`

Get issues assigned to current resolver.

**Query Parameters:**

- `status`: Filter by status
- `urgency`: Filter by urgency
- `sort`: Sort order

#### GET `/api/v1/resolver/pending/`

Get issues pending review in resolver's jurisdiction.

#### POST `/api/v1/resolver/issues/{id}/accept/`

Accept/claim an issue for resolution.

#### POST `/api/v1/resolver/issues/{id}/complete/`

Mark issue as resolved.

**Request (multipart/form-data):**

```json
{
	"resolution_note": "Pothole has been filled and road repaired.",
	"after_images": ["<file1>", "<file2>"]
}
```

---

### Admin Endpoints

#### GET `/api/v1/admin/dashboard/`

Get admin dashboard data.

**Response (200 OK):**

```json
{
    "success": true,
    "data": {
        "stats": {
            "total_users": 152,
            "active_resolvers": 24,
            "total_issues": 1204,
            "resolved_issues": 987,
            "pending_verification": 5,
            "avg_resolution_time": "36h"
        },
        "pending_approvals": [...],
        "recent_issues": [...],
        "recent_activity": [...]
    }
}
```

#### GET `/api/v1/admin/users/`

List all users (citizens).

**Query Parameters:**

- `search`: Search by name or email
- `status`: Filter by active status
- `role`: Filter by role
- `sort`: Sort order

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"results": [
			{
				"id": "user-1",
				"name": "Eleanor Vance",
				"username": "eleanor_v",
				"email": "eleanor.v@email.com",
				"avatar": "https://example.com/avatars/user-1.jpg",
				"role": "citizen",
				"is_active": true,
				"joined_at": "2023-01-15T00:00:00Z",
				"issues_count": 5
			}
		],
		"count": 150,
		"stats": {
			"total": 150,
			"active": 145,
			"suspended": 3,
			"banned": 2
		}
	}
}
```

#### GET `/api/v1/admin/users/{id}/`

Get user details (admin view).

#### PATCH `/api/v1/admin/users/{id}/`

Update user (admin).

#### POST `/api/v1/admin/users/{id}/toggle-status/`

Toggle user active status.

**Request:**

```json
{
	"is_active": false,
	"reason": "Violation of community guidelines"
}
```

#### DELETE `/api/v1/admin/users/{id}/`

Delete user.

#### GET `/api/v1/admin/resolvers/`

List all resolvers.

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"results": [
			{
				"id": "resolver-1",
				"name": "John Smith",
				"email": "john.smith@publicworks.gov",
				"avatar": "https://example.com/avatars/resolver-1.jpg",
				"department": {
					"id": "public-works",
					"name": "Public Works"
				},
				"designation": "Field Officer",
				"jurisdiction": "Ward A, Ward B",
				"is_verified": true,
				"verified_at": "2023-06-20T10:00:00Z",
				"stats": {
					"resolved": 48,
					"avg_response_time": "2.5 days"
				}
			}
		],
		"count": 24,
		"stats": {
			"total": 24,
			"verified": 20,
			"pending": 4
		}
	}
}
```

#### GET `/api/v1/admin/resolvers/pending/`

Get resolvers pending verification.

#### POST `/api/v1/admin/resolvers/{id}/verify/`

Verify resolver.

**Request:**

```json
{
	"approved": true,
	"note": "Documents verified successfully"
}
```

#### POST `/api/v1/admin/resolvers/{id}/reject/`

Reject resolver verification.

**Request:**

```json
{
	"reason": "Invalid employee ID"
}
```

#### DELETE `/api/v1/admin/resolvers/{id}/`

Remove resolver.

---

### Analytics Endpoints

#### GET `/api/v1/analytics/overview/`

Get platform analytics overview.

**Query Parameters:**

- `time_range`: 7days, 30days, 90days, 1year

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"stats": {
			"total_issues": 1204,
			"resolved": 987,
			"active_users": 152,
			"avg_resolution_time": "36h"
		},
		"trends": {
			"issues": "+12%",
			"resolved": "+8%",
			"users": "+5%",
			"resolution_time": "-15%"
		},
		"issues_by_status": [
			{ "status": "Reported", "count": 24, "percentage": 30 },
			{ "status": "Acknowledged", "count": 18, "percentage": 22 },
			{ "status": "In Progress", "count": 28, "percentage": 35 },
			{ "status": "Resolved", "count": 10, "percentage": 13 }
		],
		"issues_by_category": [
			{ "category": "Infrastructure", "count": 32, "percentage": 40 },
			{ "category": "Sanitation", "count": 22, "percentage": 28 },
			{ "category": "Safety", "count": 14, "percentage": 18 },
			{ "category": "Environment", "count": 8, "percentage": 10 },
			{ "category": "Other", "count": 4, "percentage": 4 }
		],
		"monthly_trends": [
			{ "month": "Jan", "issues": 45, "resolved": 38 },
			{ "month": "Feb", "issues": 52, "resolved": 45 },
			{ "month": "Mar", "issues": 48, "resolved": 42 }
		],
		"top_resolvers": [
			{
				"name": "Sarah Johnson",
				"department": "Public Works",
				"resolved": 45,
				"rating": 4.8
			}
		]
	}
}
```

#### GET `/api/v1/analytics/issues/`

Detailed issue analytics.

#### GET `/api/v1/analytics/users/`

User analytics.

#### GET `/api/v1/analytics/resolvers/`

Resolver performance analytics.

---

### Platform Stats Endpoint (Public)

#### GET `/api/v1/platform/stats/`

Get public platform statistics (for landing page).

**Response (200 OK):**

```json
{
	"success": true,
	"data": {
		"issues_reported": 1204,
		"issues_resolved": 987,
		"active_members": 152,
		"avg_resolution_time": "36h"
	}
}
```

---

### Settings Endpoints

#### GET `/api/v1/users/me/settings/`

Get user settings.

**Response (200 OK):**

```json
{
	"success": true,
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

#### PATCH `/api/v1/users/me/settings/`

Update user settings.

**Request:**

```json
{
	"notifications": {
		"email": false
	}
}
```

---

## Error Handling

### Standard Error Codes

| HTTP Status | Error Code              | Description                           |
| ----------- | ----------------------- | ------------------------------------- |
| 400         | VALIDATION_ERROR        | Invalid input data                    |
| 401         | AUTHENTICATION_REQUIRED | User not authenticated                |
| 401         | INVALID_TOKEN           | JWT token is invalid                  |
| 401         | TOKEN_EXPIRED           | JWT token has expired                 |
| 403         | PERMISSION_DENIED       | User lacks permission                 |
| 403         | ACCOUNT_SUSPENDED       | User account is suspended             |
| 403         | RESOLVER_NOT_VERIFIED   | Resolver account pending verification |
| 404         | NOT_FOUND               | Resource not found                    |
| 409         | DUPLICATE_ENTRY         | Resource already exists               |
| 429         | RATE_LIMIT_EXCEEDED     | Too many requests                     |
| 500         | SERVER_ERROR            | Internal server error                 |

### Error Response Examples

**Validation Error (400):**

```json
{
	"success": false,
	"message": "Validation failed",
	"errors": {
		"email": ["This email is already registered"],
		"password": ["Password must be at least 8 characters"]
	},
	"error_code": "VALIDATION_ERROR"
}
```

**Authentication Error (401):**

```json
{
	"success": false,
	"message": "Authentication credentials were not provided",
	"error_code": "AUTHENTICATION_REQUIRED"
}
```

**Permission Error (403):**

```json
{
	"success": false,
	"message": "You do not have permission to perform this action",
	"error_code": "PERMISSION_DENIED"
}
```

---

## Pagination & Filtering

### Pagination Response Format

All list endpoints should return paginated responses:

```json
{
    "success": true,
    "data": {
        "results": [...],
        "count": 100,
        "next": "https://api.townspark.com/api/v1/issues/?page=2",
        "previous": null,
        "page": 1,
        "page_size": 10,
        "total_pages": 10
    }
}
```

### Common Query Parameters

| Parameter | Type   | Description                               |
| --------- | ------ | ----------------------------------------- |
| page      | int    | Page number (default: 1)                  |
| page_size | int    | Items per page (default: 10, max: 100)    |
| search    | string | Search term                               |
| ordering  | string | Sort field (prefix with - for descending) |

### Filtering Guidelines

- Use query parameters for filtering
- Support multiple values with comma separation: `?status=reported,acknowledged`
- Support date ranges: `?created_after=2024-01-01&created_before=2024-01-31`
- Support location-based filtering: `?lat=40.7128&lng=-74.006&radius=5` (km)

---

## File Upload Guidelines

### Image Upload Specifications

- **Supported formats**: JPEG, PNG, WebP
- **Max file size**: 10MB per image
- **Max images per issue**: 5
- **Recommended dimensions**: 1200x800px minimum
- **Thumbnail generation**: Auto-generate 300x200px thumbnails

### Upload Endpoints

For file uploads, use `multipart/form-data`:

```python
# views.py
class IssueViewSet(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
```

### Image Response Format

Always return full URLs:

```json
{
	"images": [
		{
			"id": "img-1",
			"url": "https://example.com/media/issues/TS-1138/image1.jpg",
			"thumbnail": "https://example.com/media/issues/TS-1138/thumb_image1.jpg"
		}
	]
}
```

---

## WebSocket Events

For real-time notifications, implement Django Channels:

### Connection URL

```
wss://api.townspark.com/ws/notifications/?token=<access_token>
```

### Event Types

**New Notification:**

```json
{
	"type": "notification",
	"data": {
		"id": "notif-123",
		"type": "status_update",
		"title": "Status Update",
		"message": "Your issue has been acknowledged",
		"issue_id": "TS-1138",
		"created_at": "2024-01-15T10:30:00Z"
	}
}
```

**Issue Update:**

```json
{
	"type": "issue_update",
	"data": {
		"issue_id": "TS-1138",
		"status": "acknowledged",
		"updated_at": "2024-01-15T10:30:00Z"
	}
}
```

**New Comment:**

```json
{
    "type": "new_comment",
    "data": {
        "issue_id": "TS-1138",
        "comment": {...}
    }
}
```

---

## Frontend Integration Notes

### Field Mapping

The frontend expects certain field names. Ensure your serializers map correctly:

| Frontend Field        | Backend Field   | Notes                              |
| --------------------- | --------------- | ---------------------------------- |
| `author`              | `reporter`      | For issues, map reporter to author |
| `upvotes` / `uplifts` | `upvote_count`  | Computed field                     |
| `comments`            | `comment_count` | Computed field                     |
| `joined_at`           | `created_at`    | For users                          |
| `is_upvoted`          | Computed        | Check if current user upvoted      |
| `is_bookmarked`       | Computed        | Check if current user bookmarked   |

### Serializer Example

```python
class IssueListSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(source='reporter', read_only=True)
    upvotes = serializers.IntegerField(source='upvote_count', read_only=True)
    uplifts = serializers.IntegerField(source='upvote_count', read_only=True)
    comments = serializers.IntegerField(source='comment_count', read_only=True)
    location = serializers.SerializerMethodField()
    is_upvoted = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    def get_location(self, obj):
        return f"{obj.address}, {obj.area}"

    def get_is_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.upvote_records.filter(user=request.user).exists()
        return False
```

### Date Format

Always use ISO 8601 format: `2024-01-15T10:30:00Z`

```python
# settings.py
REST_FRAMEWORK = {
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%SZ',
    'DATE_FORMAT': '%Y-%m-%d',
}
```

---

## Quick Reference - All Endpoints

### Authentication

| Method | Endpoint                          | Description            |
| ------ | --------------------------------- | ---------------------- |
| POST   | `/api/v1/auth/register/`          | Register citizen       |
| POST   | `/api/v1/auth/register/resolver/` | Register resolver      |
| POST   | `/api/v1/auth/login/`             | Login                  |
| POST   | `/api/v1/auth/logout/`            | Logout                 |
| POST   | `/api/v1/auth/token/refresh/`     | Refresh token          |
| POST   | `/api/v1/auth/password/reset/`    | Request password reset |
| POST   | `/api/v1/auth/password/change/`   | Change password        |

### Users

| Method | Endpoint                      | Description           |
| ------ | ----------------------------- | --------------------- |
| GET    | `/api/v1/users/me/`           | Get current user      |
| PATCH  | `/api/v1/users/me/`           | Update current user   |
| GET    | `/api/v1/users/me/issues/`    | Get user's issues     |
| GET    | `/api/v1/users/me/bookmarks/` | Get bookmarked issues |
| GET    | `/api/v1/users/me/upvoted/`   | Get upvoted issues    |
| GET    | `/api/v1/users/me/settings/`  | Get user settings     |
| PATCH  | `/api/v1/users/me/settings/`  | Update user settings  |
| GET    | `/api/v1/users/{id}/`         | Get user profile      |

### Issues

| Method | Endpoint                                 | Description           |
| ------ | ---------------------------------------- | --------------------- |
| GET    | `/api/v1/issues/`                        | List issues (feed)    |
| POST   | `/api/v1/issues/`                        | Create issue          |
| GET    | `/api/v1/issues/{id}/`                   | Get issue details     |
| PATCH  | `/api/v1/issues/{id}/`                   | Update issue          |
| DELETE | `/api/v1/issues/{id}/`                   | Delete issue          |
| POST   | `/api/v1/issues/{id}/upvote/`            | Toggle upvote         |
| POST   | `/api/v1/issues/{id}/bookmark/`          | Toggle bookmark       |
| PATCH  | `/api/v1/issues/{id}/status/`            | Update status         |
| POST   | `/api/v1/issues/{id}/assign/`            | Assign to resolver    |
| POST   | `/api/v1/issues/{id}/official-response/` | Add official response |

### Comments

| Method | Endpoint                        | Description    |
| ------ | ------------------------------- | -------------- |
| GET    | `/api/v1/issues/{id}/comments/` | Get comments   |
| POST   | `/api/v1/issues/{id}/comments/` | Add comment    |
| POST   | `/api/v1/comments/{id}/like/`   | Toggle like    |
| DELETE | `/api/v1/comments/{id}/`        | Delete comment |

### Notifications

| Method | Endpoint                           | Description         |
| ------ | ---------------------------------- | ------------------- |
| GET    | `/api/v1/notifications/`           | Get notifications   |
| PATCH  | `/api/v1/notifications/{id}/read/` | Mark as read        |
| POST   | `/api/v1/notifications/read-all/`  | Mark all as read    |
| DELETE | `/api/v1/notifications/{id}/`      | Delete notification |

### Reference Data

| Method | Endpoint                  | Description        |
| ------ | ------------------------- | ------------------ |
| GET    | `/api/v1/categories/`     | Get categories     |
| GET    | `/api/v1/departments/`    | Get departments    |
| GET    | `/api/v1/status-options/` | Get status options |
| GET    | `/api/v1/urgency-levels/` | Get urgency levels |
| GET    | `/api/v1/platform/stats/` | Get platform stats |

### Resolver

| Method | Endpoint                                 | Description         |
| ------ | ---------------------------------------- | ------------------- |
| GET    | `/api/v1/resolver/dashboard/`            | Get dashboard       |
| GET    | `/api/v1/resolver/assigned/`             | Get assigned issues |
| GET    | `/api/v1/resolver/pending/`              | Get pending issues  |
| POST   | `/api/v1/resolver/issues/{id}/accept/`   | Accept issue        |
| POST   | `/api/v1/resolver/issues/{id}/complete/` | Complete issue      |

### Admin

| Method | Endpoint                                  | Description           |
| ------ | ----------------------------------------- | --------------------- |
| GET    | `/api/v1/admin/dashboard/`                | Get admin dashboard   |
| GET    | `/api/v1/admin/users/`                    | List users            |
| GET    | `/api/v1/admin/users/{id}/`               | Get user              |
| PATCH  | `/api/v1/admin/users/{id}/`               | Update user           |
| POST   | `/api/v1/admin/users/{id}/toggle-status/` | Toggle user status    |
| DELETE | `/api/v1/admin/users/{id}/`               | Delete user           |
| GET    | `/api/v1/admin/resolvers/`                | List resolvers        |
| GET    | `/api/v1/admin/resolvers/pending/`        | Get pending resolvers |
| POST   | `/api/v1/admin/resolvers/{id}/verify/`    | Verify resolver       |
| POST   | `/api/v1/admin/resolvers/{id}/reject/`    | Reject resolver       |
| DELETE | `/api/v1/admin/resolvers/{id}/`           | Remove resolver       |

### Analytics

| Method | Endpoint                       | Description        |
| ------ | ------------------------------ | ------------------ |
| GET    | `/api/v1/analytics/overview/`  | Get overview       |
| GET    | `/api/v1/analytics/issues/`    | Issue analytics    |
| GET    | `/api/v1/analytics/users/`     | User analytics     |
| GET    | `/api/v1/analytics/resolvers/` | Resolver analytics |

---

## Django Project Structure (Recommended)

```
townspark_backend/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── issues/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── filters.py
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── consumers.py
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   └── urls.py
│   └── core/
│       ├── __init__.py
│       ├── models.py
│       ├── serializers.py
│       └── utils.py
├── manage.py
└── requirements.txt
```

---

## Summary

This guide provides all necessary information for backend developers to create a Django REST API that seamlessly integrates with the TownSpark React frontend. By following the response structures and endpoint conventions outlined here, the frontend team can replace hardcoded dummy data with API calls without any component modifications.

**Key Points:**

1. Use consistent response format with `success`, `message`, `data`, and `meta`
2. Match field names exactly as specified (use serializer `source` attribute if needed)
3. Always return ISO 8601 formatted dates
4. Implement pagination for all list endpoints
5. Use JWT authentication with proper token refresh mechanism
6. Follow the exact response structures for each entity

For questions or clarifications, please coordinate with the frontend team.
