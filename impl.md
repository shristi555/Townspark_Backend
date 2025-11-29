# Accounts app

this will be the central app for user management and authentication.

this should only be concerned with the user model and authentication.

It should not contain any business logic or domain-specific functionality.

the app will have 3 level of users:

1. admin ( the top level user who can manage other users and has all permissions)
2. staff ( the mid level user who can manage issues and progress)
3. regular user ( the bottom level user who can create issues and view their progress)

## User Model

the user model will have the following fields:

- id: AutoField (Primary Key)
- email: EmailField (unique, required)
- password: CharField (required, hashed)
- full_name: CharField (optional)
- phone_number: CharField (optional)
- address: TextField (optional)
- profile_image: ImageField (optional)
- is_active: BooleanField (default=True)
- is_staff: BooleanField (default=False) (indicates if the user is a staff member)
- is_admin: BooleanField (default=False) (indicates if the user is an admin)
- date_joined: DateTimeField (auto_now_add=True)

### Public fields

- full_name
- address
- profile_image

only these fields should be exposed to the users via the details endpoint. this is useful fot the details lookup page on frontend.

for the auth and login the email and password fields will be used.

## Endpoints Expected

the following are the main API endpoints provided by the Accounts app, along with their expected request and response formats.

1. `POST /auth/signup/` - User Registration
2. `POST /auth/login/` - User Login (Token Creation)
3. `POST /auth/jwt/refresh/` - Token Refresh
4. `POST /auth/jwt/verify/` - Token Verification
5. `GET /auth/users/me/` - Get Current User Profile
6. `PUT /auth/users/me/` or `PATCH /auth/users/me/` - Update Current User Profile

# Response Formats

All responses should be in JSON format.

### Example response for user registration:

We return the created user object without sensitive information like password.

```json
{
	"id": 9,
	"email": "bruce.wyane@example.com",
	"full_name": "Bruce Wayne",
	"phone_number": "+9700",
	"address": "Wayne Manor, Gotham City",
	"profile_image": null
}
```

### Example response for user login:

we return the JWT tokens as well as the user object.

```json
{
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
}
```

### Example response for getting current user profile:

we just return the user object.

```json
{
	"id": 9,
	"email": "bruce.wyane@example.com",
	"full_name": "Bruce Wayne",
	"phone_number": "+9700",
	"address": "Wayne Manor, Gotham City",
	"profile_image": null
}
```

### Example response for refreshing token:

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Example response for updating current user profile:

we return the updated user object.

```json
{
	"id": 9,
	"email": "bruce.wyane@example.com",
	"full_name": "Bruce Wayne edited",
	"phone_number": "+9700123456",
	"address": "Wayne Manor, Gotham City",
	"profile_image": null
}
```

# Issue app

this app will store the issues created by users.
It will have endpoints for creating, updating, deleting, and retrieving issues.

## Endpoints Expected

the following are the main API endpoints provided by the Issue app, along with their expected request and response formats.

1. `POST /issues/new` - Create Issue
2. `GET /issues/list` - List Issues
3. `GET /issues/detail/{id}/` - Retrieve Issue
4. `PUT /issues/update/{id}/` - Update Issue
5. `DELETE /issues/delete/{id}/` - Delete Issue

# Response Formats

All responses should be in JSON format.

### Example response for creating an issue:

```json
{
	"id": 1,
	"title": "Sample Issue",
	"description": "This is a sample issue description.",
	"status": "open", // Other possible values: "in_progress", "closed", "resolved"
	"created_at": "2024-01-01T12:00:00Z",
	"updated_at": "2024-01-01T12:00:00Z",
	"created_by": {
		"id": 9,
		"email": "bruce.wyane@example.com" // this much info is enough
	},
	"resolved_by": null // or the user object who resolved it
}
```

### Example response for listing issues:

```json
[
	{
		"id": 1,
		"title": "Sample Issue 1",
		"description": "This is a sample issue description.",
		"status": "open",
		"created_at": "2024-01-01T12:00:00Z",
		"updated_at": "2024-01-01T12:00:00Z",
		"created_by": {
			"id": 9,
			"email": "bruce.wyane@example.com"
		},
		"resolved_by": null
	},
	{
		"id": 2,
		"title": "Sample Issue 2",
		"description": "This is another sample issue description.",
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

# Progress app

this app will track the progress of issues.
it will use the model of issue in the issue app, and will have endpoints for creating, updating, deleting, and retrieving progress updates related to issues.

the model of the progress app is as below:

- id: AutoField (Primary Key)
- issue: ForeignKey to Issue (the issue this progress update is related to)
- status: CharField (the current status of the issue, e.g., "in_progress", "resolved")
- updated_at: DateTimeField (the timestamp when this progress update was made)
- updated_by: ForeignKey to User (the user who made this progress update)
- image : ImageField (can be many images) (optional image related to the progress update )
- notes: TextField (optional notes about the progress update)

## Endpoints Expected

the following are the main API endpoints provided by the Progress app, along with their expected request and response formats.

1. `POST /progress/new` - Create Progress Update
2. `GET /progress/list` - List Progress Updates
3. `GET /progress/detail/{id}/` - Retrieve Progress Update
4. `PUT /progress/update/{id}/` - Update Progress Update
5. `DELETE /progress/delete/{id}/` - Delete Progress Update

# Response Formats

All responses should be in JSON format.

the user will be allowed to update the issue status but only if they are resolver (staff user)

# comments app

this app will handle comments on issues.
it will have endpoints for creating, updating, deleting, and retrieving comments related to issues.
the model of the comments app is as below:

- id: AutoField (Primary Key)
- issue: ForeignKey to Issue (the issue this comment is related to)
- user: ForeignKey to User (the user who made the comment)
- content: TextField (the content of the comment)
- created_at: DateTimeField (the timestamp when the comment was created)

## Endpoints Expected

the following are the main API endpoints provided by the Comments app, along with their expected request and response formats.

1. `POST /comments/new` - Create Comment
2. `GET /comments/list/{issue_id}/` - List Comments
3. `PUT /comments/update/{id}/` - Update Comment
   Note: only the user who created the comment can update it.
4. `DELETE /comments/delete/{id}/` - Delete Comment
   Note: only the user who created the comment or an admin can delete it.

### Helper endpoints for ease of use:

1. `GET /comments/mine/` - Retrieve Comment
    - retrieves all comments made by the currently authenticated user.

2. `GET /comments/issue/{issue_id}/` - List Comments for Issue
    - retrieves all comments related to a specific issue.

3. `GET /comments/user/{user_id}/` - List Comments by User
    - retrieves all comments made by a specific user (admin, staff only).

# Response Formats

All responses should be in JSON format.

### Example response for creating a comment:

```json
{
	"id": 1,
	"issue": {
		"id": 1,
		"title": "Sample Issue"
	},
	"user": {
		"id": 9,
		"email": "bruce.wyane@example.com"
	},
	"content": "This is a sample comment.",
	"created_at": "2024-01-01T12:00:00Z"
}
```

### Example response for listing comments for an issue:

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
			"email": "bruce.wyane@example.com"
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

### Example response for retrieving comments made by the authenticated user:

we need not to send the user field as it is automatically the authenticated user.

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

		"content": "This is a sample comment.",
		"created_at": "2024-01-01T12:00:00Z"
	},
	{
		"id": 3,
		"issue": {
			"id": 2,
			"title": "Another Issue"
		},

		"content": "This is a sample comment.",
		"created_at": "2024-01-01T12:00:00Z"
	}
]
```

# likes app

this app will handle likes on the issues.
it will have endpoints for creating, deleting, and retrieving likes related to issues.
the model of the likes app is as below:

- id: AutoField (Primary Key)
- issue: ForeignKey to Issue (the issue this like is related to)
- user: ForeignKey to User (the user who liked the issue)
- created_at: DateTimeField (the timestamp when the like was created)

## Endpoints Expected

the following are the main API endpoints provided by the Likes app, along with their expected request and response formats.

1. `POST /likes/new` - Create Like
2. `GET /likes/list/{issue_id}/` - List Likes
3. `DELETE /likes/delete/{id}/` - Delete Like
   Note: only the user who created the like can delete it.

### Helper endpoints for ease of use:

1. `GET /likes/mine/` - Retrieve Likes
    - retrieves all likes made by the currently authenticated user.

2. `GET /likes/issue/{issue_id}/` - List Likes for Issue
    - retrieves all likes related to a specific issue.

3. `GET /likes/user/{user_id}/` - List Likes by User
    - retrieves all likes made by a specific user (admin, staff only).

4. `GET /likes/count/{issue_id}/` - Count Likes for Issue
    - retrieves the total number of likes for a specific issue.

# Response Formats

All responses should be in JSON format.
