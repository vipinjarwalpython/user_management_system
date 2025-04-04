from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager to handle user creation using email instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.

        Args:
            email (str): The email address of the user.
            password (str): The password for the user.
            extra_fields (dict): Additional fields to set on the user.

        Returns:
            User: The created user object.
        """
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with admin role and elevated permissions.

        Args:
            email (str): The email address of the superuser.
            password (str): The password for the superuser.
            extra_fields (dict): Additional fields to set on the superuser.

        Returns:
            User: The created superuser object.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model using email as the unique identifier instead of username.

    Fields:
        - email: Unique identifier for login.
        - role: Role of the user (ADMIN, MANAGER, USER).
        - failed_tasks: Count of how many tasks the user failed to complete.
        - is_active: Indicates whether the user account is active.

    Notes:
        - `username` field is removed.
        - `email` is set as the USERNAME_FIELD.
    """
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("MANAGER", "Manager"),
        ("USER", "User"),
    )

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="USER")
    failed_tasks = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
