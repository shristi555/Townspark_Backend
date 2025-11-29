from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.utils import timezone


def user_profile_image_path(instance, filename):
    """Generate upload path for user profile images."""
    ext = filename.split(".")[-1]
    return f"profile_images/user_{instance.id}.{ext}"


class UserManager(BaseUserManager):
    """Custom manager for User model with email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier.
    
    User levels:
    - admin: is_admin=True (top level - can manage users and has all permissions)
    - staff: is_staff=True (mid level - can manage issues and progress)
    - regular: is_admin=False, is_staff=False (bottom level - can create issues)
    """

    # Required fields
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Inherited from AbstractBaseUser but explicitly defined
    
    # Optional fields
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?\d{7,13}$",
                message="Phone number must be between 7-13 digits",
            ),
            RegexValidator(
                regex=r"^[+\d]+$",
                message="Phone number can only contain digits or a plus sign.",
            ),
        ],
    )
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to=user_profile_image_path, blank=True, null=True
    )

    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Mid-level user (can manage issues)
    is_admin = models.BooleanField(default=False)  # Top-level user (full permissions)
    
    # Timestamp
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email is already required as USERNAME_FIELD

    def save(self, *args, **kwargs):
        """Save user, handling profile image upload for new users."""
        if not self.id:
            # First save to generate ID for profile image path
            saved_image = self.profile_image
            self.profile_image = None
            super().save(*args, **kwargs)
            self.profile_image = saved_image
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or self.email

    def get_short_name(self):
        """Return the first name of the user."""
        if self.full_name:
            return self.full_name.split(" ")[0]
        return self.email

    def get_profile_image_url(self):
        """Return the absolute URL for the profile image."""
        if self.profile_image:
            request = getattr(self, "_request", None)
            if request:
                return request.build_absolute_uri(self.profile_image.url)
            return f"{settings.MEDIA_URL}{self.profile_image.name}"
        return None

    def get_user_info(self):
        """Return user information dictionary for API responses."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "address": self.address,
            "profile_image": self.get_profile_image_url(),
        }

    def get_public_info(self):
        """Return only public fields for details lookup."""
        return {
            "full_name": self.full_name,
            "address": self.address,
            "profile_image": self.get_profile_image_url(),
        }

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

