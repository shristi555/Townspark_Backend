# Progress App

This app handles progress updates for issues within the TownSpark platform.

## Models

### Progress

Represents a progress update for an issue.

| Field       | Type              | Description                        |
| ----------- | ----------------- | ---------------------------------- |
| id          | AutoField         | Unique identifier (auto-generated) |
| issue       | ForeignKey(Issue) | Related issue                      |
| description | TextField         | Description of the progress update |
| created_at  | DateTimeField     | Timestamp when created (auto)      |
| updated_by  | ForeignKey(User)  | User who made the update           |

### ProgressImage

Stores multiple images associated with a progress update.

| Field       | Type                 | Description                        |
| ----------- | -------------------- | ---------------------------------- |
| id          | AutoField            | Unique identifier (auto-generated) |
| progress    | ForeignKey(Progress) | Related progress entry             |
| image       | ImageField           | Image file                         |
| uploaded_at | DateTimeField        | Upload timestamp (auto)            |

## API Endpoints

| Method | Endpoint                             | Description                | Auth Required              |
| ------ | ------------------------------------ | -------------------------- | -------------------------- |
| POST   | `/api/v1/progress/new/`              | Create a progress update   | Yes (reporter/admin/staff) |
| GET    | `/api/v1/progress/issue/<issue_id>/` | List progress for an issue | Yes                        |

## Permissions

Only the following users can add progress updates:

- The reporter of the issue
- Admin users (is_admin=True)
- Staff users (is_staff=True)

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

### Add Progress Update

```bash
POST /api/v1/progress/new/
{
    "issue": 1,
    "description": "Started filling the pothole with gravel."
}
```

### List Progress for an Issue

```bash
GET /api/v1/progress/issue/1/
```

## Test Cases

Run tests with:

```bash
uv run pytest issue/tests.py::TestProgressViews -v
```

The test suite covers:

- Progress addition by reporter
- Progress addition by admin/staff
- Unauthorized progress addition
- Progress listing for an issue
