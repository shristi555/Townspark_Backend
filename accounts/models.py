from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings


def user_profile_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profile_images/user_<id>/<filename>
    ext = filename.split(".")[-1]
    return f"profile_images/user_{instance.id}.{ext}"


def resolver_document_path(instance, filename):
    """Generate upload path for resolver ID documents."""
    ext = filename.split(".")[-1]
    return f"resolver_docs/user_{instance.user_id}.{ext}"


class UserRole(models.TextChoices):
    CITIZEN = 'citizen', 'Citizen'
    RESOLVER = 'resolver', 'Resolver'
    ADMIN = 'admin', 'Admin'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            # 1. Check length min of 7 and max of 13 digits (excluding +)
            RegexValidator(
                regex=r"^\+?\d{7,13}$",
                message="Phone number must be between 7-13 digits",
            ),
            # 2. Check if it contains anything other than + and digits
            RegexValidator(
                regex=r"^[+\d]+$",
                message="Phone number can only contain digits or a plus sign.",
            ),
            RegexValidator(
                regex=r"^\+?\d+$",
                message="Phone number must not contain consecutive special characters.",
            ),
        ],
    )
    address = models.TextField(blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=200, blank=True, default='')

    profile_image = models.ImageField(
        upload_to=user_profile_image_path, blank=True, null=True
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CITIZEN
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def save(self, *args, **kwargs):
        # first save to generate ID
        if not self.id:
            saved_image = self.profile_image
            self.profile_image = None
            super().save(*args, **kwargs)
            self.profile_image = saved_image

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(" ")

    def get_profile_image_url(self):
        if self.profile_image:
            request = getattr(self, "_request", None)
            if request:
                return request.build_absolute_uri(self.profile_image.url)
            else:
                # Fallback to manual construction
                return f"{settings.MEDIA_URL}{self.profile_image.name}"
        return None

    def get_user_info(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "name": self.full_name,
            "phone_number": self.phone_number,
            "phone": self.phone_number,
            "address": self.address,
            "ward": self.ward,
            "bio": self.bio,
            "location": self.location,
            "avatar": self.get_profile_image_url(),
            "profile_image": self.get_profile_image_url(),
            "role": self.role,
            "is_active": self.is_active,
            "joined_at": self.created_at.isoformat() if self.created_at else None,
            "stats": self.get_stats(),
            "badges": self.get_badges()
        }

    def get_stats(self):
        """Get user statistics."""
        issues_posted = self.issues.count() if hasattr(self, 'issues') else 0
        issues_resolved = self.issues.filter(status='resolved').count() if hasattr(self, 'issues') else 0
        uplifts_received = sum(
            issue.upvote_count for issue in self.issues.all()
        ) if hasattr(self, 'issues') else 0
        
        return {
            "issues_posted": issues_posted,
            "uplifts_received": uplifts_received,
            "issues_resolved": issues_resolved
        }

    def get_badges(self):
        """Get user badges."""
        badges = []
        if hasattr(self, 'user_badges'):
            badges = [ub.badge.name for ub in self.user_badges.select_related('badge').all()]
        return badges


class ResolverProfile(models.Model):
    """
    Extended profile for resolver users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='resolver_profile'
    )
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    designation = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    jurisdiction = models.TextField(
        help_text="Comma-separated ward names",
        blank=True,
        default=''
    )
    id_document = models.FileField(
        upload_to=resolver_document_path,
        blank=True,
        null=True
    )
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_resolvers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resolver: {self.user.full_name}"

    def get_stats(self):
        """Get resolver statistics."""
        from issues.models import Issue
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        
        assigned_issues = Issue.objects.filter(assigned_resolver=self.user)
        
        pending = assigned_issues.filter(status='reported').count()
        in_progress = assigned_issues.filter(status__in=['acknowledged', 'in-progress']).count()
        
        # Get resolved this month
        from django.utils import timezone
        from datetime import timedelta
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        resolved_this_month = assigned_issues.filter(
            status='resolved',
            resolved_at__gte=month_start
        ).count()
        
        # Calculate average response time
        resolved_with_time = assigned_issues.filter(
            status='resolved',
            resolved_at__isnull=False
        ).annotate(
            resolution_time=ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=DurationField()
            )
        )
        
        avg_time = resolved_with_time.aggregate(avg=Avg('resolution_time'))['avg']
        if avg_time:
            days = avg_time.total_seconds() / 86400
            avg_response_time = f"{days:.1f} days"
        else:
            avg_response_time = "N/A"
        
        return {
            "pending": pending,
            "in_progress": in_progress,
            "resolved_this_month": resolved_this_month,
            "avg_response_time": avg_response_time
        }


class UserBadge(models.Model):
    """
    Model for tracking earned user badges.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_badges'
    )
    badge = models.ForeignKey(
        'core.Badge',
        on_delete=models.CASCADE
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.full_name} - {self.badge.name}"
