from django.db import models


class Category(models.Model):
    """
    Category model for classifying issues.
    Examples: Road Maintenance, Garbage & Waste, Electricity, etc.
    """
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Material icon name")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Department model representing government departments.
    Examples: Public Works, Sanitation, Traffic Management, etc.
    """
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Material icon name")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Badge(models.Model):
    """
    Badge model for user achievements.
    """
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    criteria = models.JSONField(default=dict, help_text="Criteria for earning the badge")

    def __str__(self):
        return self.name
