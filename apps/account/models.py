import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.conf import settings

from .managers import UserManager


# Create your models here.


class User(AbstractUser):
    """
    Custom user model that uses email as the unique identifier.
    """

    class SecurityQuestion(models.TextChoices):
        MAIDEN_NAME = (
            "maiden_name", _("What is your mother's maiden name?")
        )
        PET_NAME = (
            "pet_name", _("What is the name of your first pet?")
        )
        CITY_BORN = (
            "city_born", _("In what city were you born?")
        )
        BIRTH_YEAR = (
            "birth_year", _("What year were you born?")
        )
        FAV_COLOR = (
            "fav_color", _("What is your favorite color?")
        )

    class AccountStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        LOCKED = "locked", _("locked")
        DELETED = "deleted", _("Deleted")

    class RoleChoices(models.TextChoices):
        CUSTOMER = "customer", _("Customer")
        ACCOUNT_EXECUTIVE = "account_executive", _("Account Executive")
        TELLER = "teller", _("Teller")
        BRANCH_MANAGER = "branch_manager", _("Branch Manager")

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    email = models.EmailField(_("Email"), unique=True, db_index=True)

    username = models.CharField(_("User name"), max_length=12, unique=True)

    security_question = models.CharField(_("Security questions"), choices=SecurityQuestion.choices, max_length=30)

    security_answer = models.CharField(_("Security answer"), max_length=100)

    account_status = models.CharField(_("Account status"), choices=AccountStatus.choices, max_length=10,
                                      default=AccountStatus.ACTIVE)

    role = models.CharField(_("Role"), choices=RoleChoices.choices, max_length=30, default=RoleChoices.CUSTOMER)

    first_name = models.CharField(_("First name"), max_length=30)

    middle_name = models.CharField(_("Middle name"), max_length=30, blank=True, null=True)

    last_name = models.CharField(_("Last name"), max_length=30)

    id_no = models.PositiveIntegerField(_("ID number"), unique=True)

    failed_login_attempts = models.PositiveIntegerField(_("Failed login attempts"), default=0)

    last_login_attempt = models.DateTimeField(_("Last login attempt"), null=True, blank=True)

    otp = models.CharField(_("OTP"), max_length=6, blank=True, null=True)

    otp_expiry = models.DateTimeField(_("OTP expiry"), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "id_no", "security_question", "security_answer"]

    def set_otp(self, otp):
        self.otp = otp
        self.otp_expiry = timezone.now() + settings.OTP_EXPIRATION_TIME
        self.save(update_fields=["otp", "otp_expiry"])

    def is_otp_valid(self, otp):
        """
        Check if the OTP is valid and not expired.
        :param otp:
        :return: True if OTP is valid, False otherwise
        """
        if self.otp == otp and timezone.now() < self.otp_expiry:
            self.otp = ""
            self.otp_expiry = None
            self.save(update_fields=["otp", "otp_expiry"])
            return True
        return False

    def handle_failed_login_attempt(self):
        """
        Handle failed login attempts.
        :return: True if the user is locked out, False otherwise
        """
        self.failed_login_attempts += 1
        self.last_login_attempt = timezone.now()

        if self.failed_login_attempts >= settings.LOGIN_ATTEMPTS_LIMIT:
            self.account_status = self.AccountStatus.LOCKED
            self.save(update_fields=["failed_login_attempts", "last_login_attempt", "account_status"])
            return True
        else:
            self.save(update_fields=["failed_login_attempts", "last_login_attempt"])
            return False

    def reset_last_login_attempt(self):
        """
        Reset the last login attempt and failed login attempts.
        :return: None
        """
        self.failed_login_attempts = 0
        self.last_login_attempt = None
        self.account_status = self.AccountStatus.ACTIVE
        self.save(update_fields=["failed_login_attempts", "last_login_attempt", "account_status"])



    @property
    def unlock_account(self):
        """
        Unlock the account after the lockout duration.
        :return: None
        """
        if self.account_status == self.AccountStatus.LOCKED:
            if timezone.now() > self.last_login_attempt + settings.LOCKOUT_DURATION:
                self.account_status = self.AccountStatus.ACTIVE
                self.failed_login_attempts = 0
                self.last_login_attempt = None
                self.save(update_fields=["account_status", "failed_login_attempts", "last_login_attempt"])
                return True
        return False

    @property
    def full_name(self):
        """
        Get the full name of the user.
        :return: Full name
        """
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]


    def has_role(self, role_name):
        """
            Check if the user has a specific role.
            :param role_name:
            :return: True if the user has the role, False otherwise
        """
        return hasattr(self, 'role') and self.role == role_name

    def __str__(self):
        """
        String representation of the user.
        :return: User email
        """
        return f"{self.full_name} - {self.get_role_display()}"
