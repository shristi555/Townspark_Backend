from django.db import models
from django.conf import settings


def issue_image_path(instance, filename):
    """Generate upload path for issue images."""
    ext = filename.split(".")[-1]
    return f"issue_images/issue_{instance.issue.id}/{filename}"


class Issue(models.Model):
    """
    Model representing an issue/complaint created by users.
    
    Issues can have four statuses:
    - open: Newly created issue
    - in_progress: Issue is being worked on
    - resolved: Issue has been resolved
    - closed: Issue has been closed
    """

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    CATEGORY_CHOICES = [
        # Infrastructure & Roads
        ("road_damage", "Road Damage / Potholes"),
        ("road_construction", "Road Construction Issue"),
        ("bridge_damage", "Bridge Damage"),
        ("footpath_damage", "Footpath / Sidewalk Damage"),
        ("speed_bump", "Speed Bump Required"),
        
        # Sanitation & Waste
        ("garbage_pile", "Garbage Pile / Littering"),
        ("garbage_collection", "Garbage Collection Issue"),
        ("illegal_dumping", "Illegal Dumping"),
        ("overflowing_bins", "Overflowing Bins"),
        ("dead_animal", "Dead Animal Removal"),
        
        # Water & Drainage
        ("water_leak", "Water Leakage"),
        ("water_supply", "Water Supply Issue"),
        ("drainage_blockage", "Drainage / Sewer Blockage"),
        ("flooding", "Flooding / Waterlogging"),
        ("open_manhole", "Open Manhole"),
        
        # Electricity & Lighting
        ("street_light", "Street Light Not Working"),
        ("power_outage", "Power Outage"),
        ("damaged_pole", "Damaged Electric Pole"),
        ("exposed_wires", "Exposed / Dangerous Wires"),
        
        # Public Spaces & Parks
        ("park_maintenance", "Park Maintenance"),
        ("playground_damage", "Playground Equipment Damage"),
        ("bench_damage", "Public Bench Damage"),
        ("tree_fallen", "Fallen Tree / Branch"),
        ("overgrown_vegetation", "Overgrown Vegetation"),
        
        # Traffic & Signage
        ("traffic_signal", "Traffic Signal Malfunction"),
        ("missing_sign", "Missing / Damaged Sign"),
        ("road_marking", "Faded Road Markings"),
        ("parking_violation", "Illegal Parking"),
        
        # Public Safety
        ("stray_animals", "Stray Animals"),
        ("abandoned_vehicle", "Abandoned Vehicle"),
        ("unsafe_building", "Unsafe / Dangerous Building"),
        ("noise_complaint", "Noise Complaint"),
        ("encroachment", "Encroachment / Illegal Construction"),
        
        # Public Facilities
        ("public_toilet", "Public Toilet Issue"),
        ("bus_stop_damage", "Bus Stop Damage"),
        ("public_tap", "Public Tap / Water Point Issue"),
        
        # Environment
        ("air_pollution", "Air Pollution"),
        ("water_pollution", "Water Body Pollution"),
        ("mosquito_breeding", "Mosquito Breeding"),
        
        # Other
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other",
        help_text="Category of the issue"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default="open"
    )
    likes_count = models.PositiveIntegerField(default=0, help_text="Number of likes for this issue")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_issues",
        help_text="The user who created this issue"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_issues",
        help_text="The staff member who resolved this issue"
    )

    class Meta:
        db_table = "issues"
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def mark_in_progress(self, user):
        """Mark issue as in progress."""
        self.status = "in_progress"
        self.save()

    def resolve(self, user):
        """Mark issue as resolved by a staff member."""
        self.status = "resolved"
        self.resolved_by = user
        self.save()

    def close(self):
        """Mark issue as closed."""
        self.status = "closed"
        self.save()

    def reopen(self):
        """Reopen a closed or resolved issue."""
        self.status = "open"
        self.resolved_by = None
        self.save()


class IssueImage(models.Model):
    """
    Model for storing multiple images related to an issue.
    """
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="The issue this image belongs to"
    )
    image = models.ImageField(
        upload_to=issue_image_path,
        help_text="The uploaded image file"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "issue_images"
        verbose_name = "Issue Image"
        verbose_name_plural = "Issue Images"
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for Issue {self.issue.id}"
