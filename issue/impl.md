# issue app

this app will handle issue reporting, categorization, and management within the TownSpark platform.

## Models

- Category: Represents different categories of issues (e.g., potholes, streetlight outages).
- Issue: Represents an individual issue reported by a user, linked to a category.
- Progress : Represents the progress updates for an issue. each progress entry is linked to an issue

### Issue model

this model is the main model where the user posted issues are stored. it has fields like title, description, location, status, created_at, updated_at, category (ForeignKey to Category model), reported_by (ForeignKey to User model).

#### Fields:

- title: the title of the issue. (e.g., "Pothole on Main St.")
- description: a detailed description of the issue. (e.g., "There is a large pothole on Main St. near the intersection with 1st Ave. it is causing damage to vehicles.")
- location: the location where the issue was observed. (e.g., "Main St. near 1st Ave.")
- status: the current status of the issue (e.g., "open", "in progress", "resolved", "closed").
- created_at: the timestamp when the issue was created. (e.g., "2023-10-01 14:30:00", auto derived by backend).
- updated_at: the timestamp when the issue was last updated. (e.g., "2023-10-02 10:15:00", auto derived by backend it will also be updated when new progress is added).
- category: a foreign key linking to the Category model.
- reported_by: a foreign key linking to the User model.

### Progress model

this model is used to track the progress of an issue. each progress entry is linked to an issue and contains fields like update_text, timestamp, updated_by (ForeignKey to User model). one issue can have multiple progress entries. and each progress entry will be stored as seperate row in the database.

#### Fields:

- issue: a foreign key linking to the Issue model.
- description: a detailed description of the progress update. (e.g., "The gravel is being filled in the pothole.")
- timestamp: the timestamp when the progress update was created. (e.g., "2023-10-02 10:15:00", auto derived by backend).
- updated_by: a foreign key linking to the User model who made the progress update. (the user must be either the reporter of the issue or an admin/staff user if some other tries to update then we wont allow them).
- images: optional field to upload images related to the progress update. (multiple images can be uploaded for each progress update ).
- created_at: the timestamp when the progress entry was created. (e.g., "2023-10-02 10:15:00", auto derived by backend).

### Category model

this model is used to categorize issues. it has fields like name, description and a id.
the categories help in organizing issues and make it easier for users to report and for admins to manage them.
we will pre-define some categories like potholes, streetlight outages, graffiti, etc. and store them in the database.
only the admin will have the ability to add, update or delete categories. everyone can view the list of categories when reporting an issue.

we dont need created_at or updated_at fields for this model as categories are relatively static and dont change often ever.

#### Fields:

- name: the name of the category. (e.g., "Potholes").
- description: a brief description of the category. (e.g., "Issues related to potholes on roads.").
- id: unique identifier for each category (auto derived by backend).

## Serializers

We will have some simple serializers for the models defined above.
the user field will only have minimal fields like id, full_name and profile_image.

### Minimal User Serializer

this serializer will be used to represent minimal user info that is enough to identify the user without exposing sensitive information.

it will expose the following fields:

- id: unique identifier for the user.
- full_name: full name of the user.
- profile_image: url to the profile image of the user.

all of these fields will be read-only.

### Category Serializer

this serializer will be used to represent the category model.

it will expose the following fields: (all fields are read-only)

- id: unique identifier for the category.
- name: name of the category.
- description: brief description of the category.

this serializer will be read-only as categories are managed by admin only.

### Category Create Serializer

this serializer will be used by admin to create new categories.
it will expose the following fields:

- name: name of the category.
- description: brief description of the category.

all fields are required.

### Issue Serializer

this serializer will be used to represent the issue model.
it will expose the following fields: (all fields are read-only except status)

- id: unique identifier for the issue.
- title: title of the issue.
- description: detailed description of the issue.
- location: location where the issue was observed.
- images: list of image urls associated with the issue(if none then empty list).
- status: current status of the issue. (this field can be updated by admin/staff only).
- created_at: timestamp when the issue was created.
- updated_at: timestamp when the issue was last updated.
- category: nested representation of the category using Category Serializer.
- reported_by: nested representation of the user using Minimal User Serializer.

### Issue Create Serializer

this serializer will be used by users to create new issues.
they will provide the following fields:

- title: title of the issue.
- description: detailed description of the issue.
- location: location where the issue was observed.
- images: list of image files to be uploaded associated with the issue (optional).
- category: id of the category to which the issue belongs.

all fields are required except images.

### Progress Serializer

this serializer will be used to represent the progress model.
it will expose the following fields: (all fields are read-only)

- id: unique identifier for the progress entry.
- issue: id of the issue to which this progress entry belongs.
- description: detailed description of the progress update.
- timestamp: timestamp when the progress update was created.
- updated_by: nested representation of the user using Minimal User Serializer.
- images: list of image urls associated with the progress update (if none then empty list).

### Progress Create Serializer

this serializer will be used by admin/staff or the reporter of the issue to add progress updates.
they will provide the following fields:

- issue: id of the issue to which this progress entry belongs.
- description: detailed description of the progress update.
- images: list of image files to be uploaded associated with the progress update (optional).

all fields are required except images.

## Views

we will have views for listing, creating, retrieving, updating issues and progress entries.
the views will use the serializers defined above to handle data representation and validation.

### Issue Views

- IssueCreateView: to list all issues and create new issues.
- SpecificIssueDetailsView: to retrieve a specific issue by id.
- UserReportedIssuesView: to list all issues reported by the authenticated user.
- IssueUpdateView: to update the status of a specific issue (admin/staff or the reporter).

### Progress Views

- ProgressCreateView: to add progress updates to an issue.(only admin/staff or the reporter).
- IssueProgressListView: to list all progress updates for a specific issue.

### Category Views

- CategoryListView: to list all categories.
- CategoryCreateView: to create new categories (admin only).

## Permissions

we will implement custom permissions to ensure that only authorized users can perform certain actions.

these permissions can be applied to the views as decorators (e.g. @admin_access_only, @staff_access_only).

### Admin Access Only (@admin_access_only)

this permission will allow access only to admin users. it will check if the user is authenticated and has is_admin flag set to true in his user model.

example usage: creating categories, updating issue status, adding progress updates.

### Staff Access Only (@staff_access_only)

this permission will allow access only to staff users. it will check if the user is authenticated and has is_staff flag set to true in his user model.

example usage: updating issue status, adding progress updates.

the above were some all app usable permissions. now we will define some specific permissions for issue and progress views.

### Reporter Or Admin/Staff (@reporter_or_admin_staff)

this permission will allow access to either the reporter of the issue or admin/staff users. it will check if the user is authenticated and is either the reporter of the issue or has is_admin/is_staff flag set to true in his user model.

### Reporter Only (@reporter_only)

this permission will allow access only to the reporter of the issue. it will check if the user is authenticated and is the reporter of the issue.

example usage: deleting an issue reported by the user (if allowed).

### Admin/Staff Only (@admin_staff_only)

this permission will allow access only to admin/staff users. it will check if the user is authenticated and has is_admin/is_staff flag set to true in his user model.

example usage: adding progress updates to an issue.

## Urls

the app will expose the following urls:

- POST /issues/new/ : create a new issue.
- GET /issues/list/ : list all issues.
- GET /issues/info/<int:issue_id>/ : retrieve a specific issue by id.
- GET /issues/user/<int:user_id>/ : list all issues reported by the authenticated user.
- PATCH /issues/update/<int:issue_id>/ : update the status of a specific issue (admin/staff or the reporter).

- POST /progress/new/ : add progress updates to an issue.(only admin/staff or the reporter).
- GET /progress/issue/<int:issue_id>/ : list all progress updates for a specific issue.

- GET /categories/list/ : list all categories.
- POST /categories/new/ : create new categories (admin only).

## Response Structure

Our all response goes through a common response structure to maintain consistency across the API.
it follows something i call SER format (status, error, response).

- status: boolean indicating success (true) or failure (false) of the request.
- error: contains error details if the request failed; null otherwise.
- response: contains the actual data returned by the API if the request was successful; null otherwise.

this we dont need to implement this model in each view we will return the response normally as we will otherwise do, this wrapping is done by a middleware so that we dont have to change the views and keep the code clean.

## Test cases

we will write test cases to cover the main functionalities of the app.

- test_new_issue_creation: test creating a new issue.
- test_issue_list_view: test listing all issues.
- test_specific_issue_retrieval: test retrieving a specific issue by id.
- test_user_reported_issues: test listing all issues reported by the authenticated user.
- test_issue_status_update: test updating the status of a specific issue (admin/staff or the reporter).
- test_progress_addition_by_reporter: test adding progress updates to an issue.(by the reporter).
- test_progress_addition_by_admin_staff: test adding progress updates to an issue.(by admin/staff).
- test_issue_progress_list_view: test listing all progress updates for a specific issue.
- test_category_list_view: test listing all categories.
- test_category_creation_by_admin: test creating new categories (by admin).
- test_category_creation_by_non_admin: test creating new categories (by non-admin should fail).

these test cases will ensure that the main functionalities of the app are working as expected and that the permissions are enforced correctly.

when writing the tests we use pytest and pytest-django for testing the django app.
we will print the response data in a pretty json format for better readability and debugging.

if some test case fails we can easily identify the issue by looking at the printed response data.
