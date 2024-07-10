from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog
import uuid


# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Defines how the User (or the model to which attached)
    will create users and superusers.
    """

    def create_user(
        self,
        username=None,
        email=None,
        middle_name=None,
        password=None,
        **extra_fields,
    ):
        """Create and save a User with the given email and password."""
        if not email:
            email = f"{username}@gmail.com"
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(
            username=username,
            email=email,
            middle_name=middle_name,
            **extra_fields,
        )
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        username,
        email,
        password,
        middle_name=None,
        **extra_fields,
    ):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(
            username=username,
            email=email,
            password=password,
            middle_name=middle_name,
            **extra_fields,
        )


class CustomUser(AbstractUser):
    """Custom User model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # username = None  # ensure no username field
    email = models.EmailField(_("email address"), unique=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True, auto_now=True)

    # Make email field the unique identifier for users
    # USERNAME_FIELD = "email"
    objects = CustomUserManager()
    REQUIRED_FIELDS = [
        "email",
        "first_name",
        "last_name",
    ]

    class Meta:
        """Meta."""

        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["email"]

    def __str__(self):
        """Return string representation of user."""
        return self.email


auditlog.register(CustomUser)
