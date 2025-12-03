# new update in accounts

the accounts app need an update.
this update will not affect the existing functionality of the app. and will not touch the existing compaitibility.

this update will only add new features to the app.

the new features are:

- User profile management,

this update will add the ability for users to manage their profiles, including updating personal information and profile pictures.

it will expose some api endpoints for profile management.

## API Endpoints

- PUT /api/v1/accounts/update-profile/ : Update user profile information.
- GET /api/v1/accounts/profile/mine : Retrieve user profile information but with the other infos like issues reported etc.
- GET /api/v1/accounts/profile/<user_id>/ : Retrieve another user's profile information.

response format for these endpoints will follow the SER (Success, Error, Response) format used in other apps.

```json
{
    "success": true,
    "response": { ... },
    "error": null
}
```

### get user profile

```json
{
	"success": true,
	"response": {
		"user": "<return the normal user info as we would do during me api or login>",
		"issues_reported": "<number of issues reported by the user>",
		"progress_updates": "<number of progress updates made by the user>",
		"issues": "<list of issues reported by the user with basic info>"
	},
	"error": null
}
```
