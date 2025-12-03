from django.db import models
from django.conf import settings


def issue_image_path(instance, filename):
    """Generate upload path for issue images."""
    ext = filename.split(".")[-1]
    return f"issue_images/issue_{instance.issue.id}/{instance.id}.{ext}"


class Category(models.Model):
    """
    Model representing a category for issues.
    
    Categories help organize issues and make it easier for users to report
    and for admins to manage them. Examples: potholes, streetlight outages, graffiti.
    Only admins can add, update, or delete categories.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the category (e.g., 'Potholes')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="A brief description of the category"
    )

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Issue(models.Model):
    """
    Model representing an issue reported by a user.
    
    Issues are the main entity in the TownSpark platform where users can
    report problems in their community like potholes, streetlight outages, etc.
    """

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    title = models.CharField(
        max_length=255,
        help_text="The title of the issue (e.g., 'Pothole on Main St.')"
    )
    description = models.TextField(
        help_text="A detailed description of the issue"
    )
    location = models.CharField(
        max_length=500,
        help_text="The location where the issue was observed"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        help_text="The current status of the issue"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="issues",
        help_text="The category of the issue"
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reported_issues",
        help_text="The user who reported this issue"
    )

    class Meta:
        db_table = "issues"
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.status}"


class IssueImage(models.Model):
    """
    Model for storing multiple images associated with an issue.
    """

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="The issue this image belongs to"
    )
    image = models.ImageField(
        upload_to="issue_images/",
        help_text="Image related to the issue"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "issue_images"
        verbose_name = "Issue Image"
        verbose_name_plural = "Issue Images"
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for Issue #{self.issue.id}"
