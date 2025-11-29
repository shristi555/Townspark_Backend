# Townspark Backend

A comprehensive Django REST Framework backend for the Townspark application - a civic issue tracking and management system. This platform enables citizens to report issues in their community and allows staff members to track progress and resolve them.

## 🌟 Features

- **User Authentication**: JWT-based authentication with email login
- **Role-Based Access Control**: Three user levels (Admin, Staff, Regular User)
- **Issue Management**: Create, track, and resolve community issues
- **Progress Tracking**: Staff members can post progress updates with images
- **Comments System**: Users can discuss issues through comments
- **RESTful API**: Clean, well-documented API endpoints

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
    - [Authentication](#authentication-endpoints)
    - [Issues](#issue-endpoints)
    - [Progress](#progress-endpoints)
    - [Comments](#comment-endpoints)
- [User Roles & Permissions](#-user-roles--permissions)
- [Database Schema](#-database-schema)

---

## 🛠 Tech Stack

| Technology            | Version | Purpose                |
| --------------------- | ------- | ---------------------- |
| Python                | 3.12+   | Programming Language   |
| Django                | 5.2.8   | Web Framework          |
| Django REST Framework | 3.x     | API Framework          |
| Simple JWT            | -       | JWT Authentication     |
| SQLite                | -       | Database (Development) |
| Pillow                | -       | Image Processing       |

---

## 📁 Project Structure

```
townspark_backend/
├── main_app/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # User management & authentication
│   ├── models.py          # Custom User model
│   ├── views.py           # Auth views (signup, login, profile)
│   ├── serializers.py
│   └── urls.py
├── issue/                  # Issue/complaint management
│   ├── models.py          # Issue model
│   ├── views.py           # CRUD operations
│   ├── serializers.py
│   └── urls.py
├── progress/               # Progress tracking for issues
│   ├── models.py          # Progress & ProgressImage models
│   ├── views.py           # Staff-only progress updates
│   ├── serializers.py
│   └── urls.py
├── comment/                # Comments on issues
│   ├── models.py          # Comment model
│   ├── views.py           # Comment CRUD
│   ├── serializers.py
│   └── urls.py
├── manage.py
├── pyproject.toml
└── db.sqlite3
```

---

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- pip or uv package manager

### Setup Steps

1. **Clone the repository**

    ```bash
    git clone https://github.com/shristi555/Townspark_Backend.git
    cd Townspark_Backend
    ```

2. **Create virtual environment**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    # or using uv
    uv sync
    ```

4. **Run migrations**

    ```bash
    python manage.py migrate
    ```

5. **Create superuser (Admin)**

    ```bash
    python manage.py createsuperuser
    ```

6. **Run development server**
    ```bash
    python manage.py runserver
    ```

The API will be available at `http://localhost:8000/api/v1/`

---

## ⚙ Configuration

### JWT Settings

```python
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

### Authentication

All protected endpoints require the JWT token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

---

## 📚 API Documentation

**Base URL:** `http://localhost:8000/api/v1/`

### Authentication Endpoints

| Method    | Endpoint             | Description                 | Auth Required |
| --------- | -------------------- | --------------------------- | ------------- |
| POST      | `/auth/signup/`      | Register new user           | ❌            |
| POST      | `/auth/login/`       | Login & get tokens          | ❌            |
| POST      | `/auth/jwt/refresh/` | Refresh access token        | ❌            |
| POST      | `/auth/jwt/verify/`  | Verify token validity       | ❌            |
| GET       | `/auth/users/me/`    | Get current user profile    | ✅            |
| PUT/PATCH | `/auth/users/me/`    | Update current user profile | ✅            |

#### Register User

```http
POST /api/v1/auth/signup/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "address": "123 Main St, City"
}
```

**Response (201 Created):**

```json
{
	"id": 1,
	"email": "user@example.com",
	"full_name": "John Doe",
	"phone_number": "+1234567890",
	"address": "123 Main St, City",
	"profile_image": null
}
```

#### Login

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response (200 OK):**

```json
{
	"tokens": {
		"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
		"access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
	},
	"user": {
		"id": 1,
		"email": "user@example.com",
		"full_name": "John Doe",
		"phone_number": "+1234567890",
		"address": "123 Main St, City",
		"profile_image": null
	}
}
```

#### Refresh Token

```http
POST /api/v1/auth/jwt/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Issue Endpoints

| Method    | Endpoint               | Description       | Auth Required |
| --------- | ---------------------- | ----------------- | ------------- |
| POST      | `/issues/new/`         | Create new issue  | ✅            |
| GET       | `/issues/list/`        | List issues       | ✅            |
| GET       | `/issues/detail/{id}/` | Get issue details | ✅            |
| PUT/PATCH | `/issues/update/{id}/` | Update issue      | ✅            |
| DELETE    | `/issues/delete/{id}/` | Delete issue      | ✅            |

#### Create Issue

```http
POST /api/v1/issues/new/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Pothole on Main Street",
    "description": "Large pothole causing traffic issues near the intersection."
}
```

**Response (201 Created):**

```json
{
	"id": 1,
	"title": "Pothole on Main Street",
	"description": "Large pothole causing traffic issues near the intersection.",
	"status": "open",
	"created_at": "2024-01-01T12:00:00Z",
	"updated_at": "2024-01-01T12:00:00Z",
	"created_by": {
		"id": 1,
		"email": "user@example.com"
	},
	"resolved_by": null
}
```

#### List Issues

```http
GET /api/v1/issues/list/
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `status` - Filter by status (open, in_progress, resolved, closed)

**Response (200 OK):**

```json
[
	{
		"id": 1,
		"title": "Pothole on Main Street",
		"description": "Large pothole causing traffic issues.",
		"status": "open",
		"created_at": "2024-01-01T12:00:00Z",
		"updated_at": "2024-01-01T12:00:00Z",
		"created_by": {
			"id": 1,
			"email": "user@example.com"
		},
		"resolved_by": null
	}
]
```

#### Issue Status Values

| Status        | Description                   |
| ------------- | ----------------------------- |
| `open`        | Newly created issue (default) |
| `in_progress` | Issue is being worked on      |
| `resolved`    | Issue has been resolved       |
| `closed`      | Issue has been closed         |

---

### Progress Endpoints

| Method    | Endpoint                      | Description               | Auth Required | Staff Only |
| --------- | ----------------------------- | ------------------------- | ------------- | ---------- |
| POST      | `/progress/new/`              | Create progress update    | ✅            | ✅         |
| GET       | `/progress/list/`             | List all progress updates | ✅            | ❌         |
| GET       | `/progress/detail/{id}/`      | Get progress details      | ✅            | ❌         |
| PUT/PATCH | `/progress/update/{id}/`      | Update progress           | ✅            | ✅         |
| DELETE    | `/progress/delete/{id}/`      | Delete progress           | ✅            | ✅         |
| GET       | `/progress/issue/{issue_id}/` | Get progress for issue    | ✅            | ❌         |

#### Create Progress Update

```http
POST /api/v1/progress/new/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
    "issue_id": 1,
    "status": "in_progress",
    "notes": "Work has started on fixing the pothole.",
    "images": [<file1>, <file2>]  // Optional
}
```

**Response (201 Created):**

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Pothole on Main Street"
	},
	"status": "in_progress",
	"notes": "Work has started on fixing the pothole.",
	"updated_at": "2024-01-02T10:00:00Z",
	"updated_by": {
		"id": 2,
		"email": "staff@example.com"
	},
	"images": [
		{
			"id": 1,
			"image": "/media/progress_images/issue_1/progress_1_1.jpg"
		}
	]
}
```

#### Get Progress for Issue

```http
GET /api/v1/progress/issue/1/
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
[
	{
		"id": 1,
		"issue": {
			"id": 1,
			"title": "Pothole on Main Street"
		},
		"status": "in_progress",
		"notes": "Work has started.",
		"updated_at": "2024-01-02T10:00:00Z",
		"updated_by": {
			"id": 2,
			"email": "staff@example.com"
		},
		"images": []
	}
]
```

---

### Comment Endpoints

| Method    | Endpoint                      | Description                       | Auth Required |
| --------- | ----------------------------- | --------------------------------- | ------------- |
| POST      | `/comments/new/`              | Create comment                    | ✅            |
| GET       | `/comments/list/{issue_id}/`  | List comments for issue           | ✅            |
| PUT/PATCH | `/comments/update/{id}/`      | Update comment (owner only)       | ✅            |
| DELETE    | `/comments/delete/{id}/`      | Delete comment (owner/admin)      | ✅            |
| GET       | `/comments/mine/`             | Get my comments                   | ✅            |
| GET       | `/comments/issue/{issue_id}/` | Get comments by issue             | ✅            |
| GET       | `/comments/user/{user_id}/`   | Get comments by user (staff only) | ✅            |

#### Create Comment

```http
POST /api/v1/comments/new/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "issue_id": 1,
    "content": "Is there an estimated timeline for this fix?"
}
```

**Response (201 Created):**

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Pothole on Main Street"
	},
	"user": {
		"id": 1,
		"email": "user@example.com"
	},
	"content": "Is there an estimated timeline for this fix?",
	"created_at": "2024-01-01T14:00:00Z"
}
```

#### Get My Comments

```http
GET /api/v1/comments/mine/
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
[
	{
		"id": 1,
		"issue": {
			"id": 1,
			"title": "Pothole on Main Street"
		},
		"content": "Is there an estimated timeline for this fix?",
		"created_at": "2024-01-01T14:00:00Z"
	}
]
```

---

## 👥 User Roles & Permissions

### User Levels

| Level       | Field Values                     | Description                          |
| ----------- | -------------------------------- | ------------------------------------ |
| **Admin**   | `is_admin=True`                  | Full system access, can manage users |
| **Staff**   | `is_staff=True`                  | Can manage issues and progress       |
| **Regular** | `is_admin=False, is_staff=False` | Can create issues and comments       |

### Permissions Matrix

| Action             | Regular User | Staff | Admin |
| ------------------ | ------------ | ----- | ----- |
| **Issues**         |              |       |       |
| Create Issue       | ✅           | ✅    | ✅    |
| View Own Issues    | ✅           | ✅    | ✅    |
| View All Issues    | ❌           | ✅    | ✅    |
| Update Own Issue   | ✅           | ✅    | ✅    |
| Update Any Issue   | ❌           | ✅    | ✅    |
| Delete Own Issue   | ✅           | ✅    | ✅    |
| Delete Any Issue   | ❌           | ✅    | ✅    |
| Mark as Resolved   | ❌           | ✅    | ✅    |
| **Progress**       |              |       |       |
| View Progress      | ✅           | ✅    | ✅    |
| Create Progress    | ❌           | ✅    | ✅    |
| Update Progress    | ❌           | ✅    | ✅    |
| Delete Progress    | ❌           | ✅    | ✅    |
| **Comments**       |              |       |       |
| Create Comment     | ✅           | ✅    | ✅    |
| View Comments      | ✅           | ✅    | ✅    |
| Update Own Comment | ✅           | ✅    | ✅    |
| Delete Own Comment | ✅           | ✅    | ✅    |
| Delete Any Comment | ❌           | ✅    | ✅    |
| View User Comments | ❌           | ✅    | ✅    |

---

## 🗄 Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │
├─────────────────────┤
│ id (PK)             │
│ email (unique)      │
│ password            │
│ full_name           │
│ phone_number        │
│ address             │
│ profile_image       │
│ is_active           │
│ is_staff            │
│ is_admin            │
│ date_joined         │
└─────────┬───────────┘
          │
          │ 1:N
          ▼
┌─────────────────────┐       ┌─────────────────────┐
│       Issue         │       │      Comment        │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────│ id (PK)             │
│ title               │  1:N  │ issue (FK)          │
│ description         │       │ user (FK)           │
│ status              │       │ content             │
│ created_at          │       │ created_at          │
│ updated_at          │       └─────────────────────┘
│ created_by (FK)     │
│ resolved_by (FK)    │
└─────────┬───────────┘
          │
          │ 1:N
          ▼
┌─────────────────────┐       ┌─────────────────────┐
│      Progress       │       │   ProgressImage     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────│ id (PK)             │
│ issue (FK)          │  1:N  │ progress (FK)       │
│ status              │       │ image               │
│ notes               │       └─────────────────────┘
│ updated_at          │
│ updated_by (FK)     │
└─────────────────────┘
```

### Tables

| Table             | Description                 |
| ----------------- | --------------------------- |
| `auth_user`       | Custom user accounts        |
| `issues`          | Issue/complaint records     |
| `progress`        | Progress updates on issues  |
| `progress_images` | Images attached to progress |
| `comments`        | Comments on issues          |

---

## 🔄 Issue Status Workflow

```
┌─────────────┐
│    open     │ ◄─── New issue created by user
└──────┬──────┘
       │
       ▼ (Staff action)
┌─────────────┐
│ in_progress │ ◄─── Staff starts working
└──────┬──────┘
       │
       ▼ (Staff action)
┌─────────────┐
│  resolved   │ ◄─── Staff marks as resolved (resolved_by set)
└──────┬──────┘
       │
       ▼ (Staff action)
┌─────────────┐
│   closed    │ ◄─── Issue closed
└─────────────┘
```

---

## 🧪 Testing

Run tests with:

```bash
python manage.py test
```

Or with pytest:

```bash
pytest
```

---

## 📄 Individual App Documentation

For detailed documentation on each app, see:

- [Accounts App](./accounts/README.md) - User management & authentication
- [Issue App](./issue/README.md) - Issue/complaint management
- [Progress App](./progress/README.md) - Progress tracking
- [Comment App](./comment/README.md) - Comments system

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 👤 Author

**Shristi** - [GitHub](https://github.com/shristi555)
