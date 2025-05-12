import random
import string
from os import getenv
from typing import Any

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def generate_username() -> str:
    """
    Generate a random username.
    :return: A random username
    """
    bank_name = getenv("BANK_NAME")
    words = bank_name.split()
    prefix = "".join(word[0] for word in words)
    remaining_characters = 12 - len(prefix) - 1
    random_string = "".join(random.choices(string.ascii_uppercase + string.digits, k=remaining_characters))
    username = f"{prefix}-{random_string}"
    return username


def validate_email(email: str) -> None:
    """
    Validate the email address.
    :param email:
    :return: Validate email address
    """
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError(_("Invalid email address"))


class UserManager(DjangoUserManager):
    """
    Custom user manager for User model.
    """

    def _create_user(self, email: str, password: str, **extra_fields: Any):
        """
        Create and return a `User` with an email and password.
        :param email:
        :param password:
        :param extra_fields:
        :return: A user with the given email and password
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        if not password:
            raise ValueError(_("The Password field must be set"))

        email = self.normalize_email(email)
        validate_email(email)
        username = generate_username()
        user = self.model(email=email, username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str = None, **extra_fields: Any):
        """
        Create and return a `User` with an email and password.
        :param email:
        :param password:
        :param extra_fields:
        :return: User with the given email and password
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str = None, **extra_fields: Any):
        """
        Create and return a `User` with superuser (admin) permissions.
        :param email:
        :param password:
        :param extra_fields:
        :return: User with superuser (admin) permissions
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if extra_fields.get("is_active") is not True:
            raise ValueError(_("Superuser must have is_active=True."))
        return self._create_user(email, password, **extra_fields)
