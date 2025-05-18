import uuid

from cloudinary.models import CloudinaryField
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

from .managers import UserManager
from ..core.models import TimeStampedModel


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

    def reset_failed_login_attempt(self):
        """
        Reset the last login attempt and failed login attempts.
        :return: None
        """
        self.failed_login_attempts = 0
        self.last_login_attempt = None
        self.account_status = self.AccountStatus.ACTIVE
        self.save(update_fields=["failed_login_attempts", "last_login_attempt", "account_status"])

    @property
    def is_locked_out(self):
        """
        Checks if the account is currently locked out.
        If the lockout duration has expired, unlocks the account.
        :return: Boolean indicating if the account is still locked out
        """
        if self.account_status == self.AccountStatus.LOCKED:
            # Check if lockout duration has expired
            if timezone.now() > self.last_login_attempt + settings.LOCKOUT_DURATION:
                # Unlock the account
                self.account_status = self.AccountStatus.ACTIVE
                self.failed_login_attempts = 0
                self.last_login_attempt = None
                self.save(update_fields=["account_status", "failed_login_attempts", "last_login_attempt"])
                return False
            else:
                return True
        return False

    def set_security_answer(self, raw_answer):
        """
        Sets a hashed security answer
        """
        self.security_answer = make_password(raw_answer)

    def check_security_answer(self, raw_answer):
        """
        Checks if the provided answer matches the stored security answer
        """
        return check_password(raw_answer, self.security_answer)

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




class Profile(TimeStampedModel):
    """
    User profile model.
    """
    class SalutationChoice(models.TextChoices):
        MR = "mr", _("Mr.")
        MRS = "mrs", _("Mrs.")
        MS = "ms", _("Ms.")
        DR = "dr", _("Dr.")
        PROF = "prof", _("Prof.")
    class GenderChoice(models.TextChoices):
        MALE = ("Male", _("Male"))
        FEMALE = ("Female", _("Female"))

    class MaritalStatusChoice(models.TextChoices):
        SINGLE = ("Single", _("Single"))
        MARRIED = ("Married", _("Married"))
        DIVORCED = ("Divorced", _("Divorced"))
        WIDOWED = ("Widowed", _("Widowed"))

    class IdentificationTypeChoice(models.TextChoices):
        PASSPORT = ("Passport", _("Passport"))
        ID_CARD = ("ID Card", _("ID Card"))
        DRIVER_LICENSE = ("Driver License", _("Driver License"))
        NATIONAL_ID = ("National ID", _("National ID"))
        OTHER = ("Other", _("Other"))

    class EmploymentChoice(models.TextChoices):
        EMPLOYED = ("Employed", _("Employed"))
        UNEMPLOYED = ("Unemployed", _("Unemployed"))
        SELF_EMPLOYED = ("Self Employed", _("Self Employed"))
        RETIRED = ("Retired", _("Retired"))
        STUDENT = ("Student", _("Student"))


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    title=models.CharField(_("Salutation"), choices=SalutationChoice.choices, default=SalutationChoice.MR, max_length=5)

    gender= models.CharField(_("Gender"), choices=GenderChoice.choices, default=GenderChoice.MALE, max_length=10)

    marital_status = models.CharField(_("Marital status"), choices=MaritalStatusChoice.choices, default=MaritalStatusChoice.MARRIED, max_length=10)

    phone_number = PhoneNumberField(_("Phone number"), max_length=15, blank=True, null=True, default=settings.DEFAULT_PHONE_NUMBER)

    address = models.TextField(_("Address"), blank=True, null=True)

    date_of_birth = models.DateField(_("Date of birth"), blank=True, null=True, default=settings.DEFAULT_BIRTH_DATE)

    identification_type = models.CharField(_("Identification type"), choices=IdentificationTypeChoice.choices, default=IdentificationTypeChoice.ID_CARD, max_length=20)

    country_of_birth = CountryField(_("Country"), blank=True, null=True, default=settings.DEFAULT_COUNTRY)

    place_of_birth = models.CharField(_("Place of birth"), max_length=100, default="Unknown")

    id_issue_date = models.DateField(_("ID issue date"), blank=True, null=True, default=settings.DEFAULT_DATE)

    id_expiry_date = models.DateField(_("ID expiry date"), blank=True, null=True, default=settings.DEFAULT_EXPIRY_DATE)

    employment_status = models.CharField(_("Employment status"), choices=EmploymentChoice.choices, default=EmploymentChoice.UNEMPLOYED, max_length=20)

    passport_number = models.CharField(_("Passport number"), max_length=20, blank=True, null=True)

    nationality = CountryField(_("Nationality"), blank=True, null=True, default=settings.DEFAULT_COUNTRY)

    city = models.CharField(_("City"), max_length=100, blank=True, null=True)

    employer_name = models.CharField(_("Employer name"), max_length=100, blank=True, null=True)

    annual_income = models.DecimalField(_("Annual income"), max_digits=15, decimal_places=2, blank=True, null=True)

    date_of_employment = models.DateField(_("Date of employment"), blank=True, null=True)

    employer_address = models.TextField(_("Employer address"), blank=True, null=True)

    employer_city = models.CharField(_("Employer city"), max_length=100, blank=True, null=True)

    employer_state = models.CharField(_("Employer state"), max_length=100, blank=True, null=True)

    photo = CloudinaryField(_("Photo"), blank=True, null=True)

    photo_url = models.URLField(_("Photo URL"), blank=True, null=True)

    id_photo = CloudinaryField(_("ID Photo"), blank=True, null=True)

    id_photo_url = models.URLField(_("ID Photo URL"), blank=True, null=True)

    signature_photo = CloudinaryField(_("Signature Photo"), blank=True, null=True)

    signature_photo_url = models.URLField(_("Signature Photo URL"), blank=True, null=True)


    def clean(self):
        """
        Clean the profile data.
        :return: None
        """
        super().clean()
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError(_("Date of birth cannot be in the future."))

        if self.id_issue_date and self.id_issue_date > timezone.now().date():
            raise ValidationError(_("ID issue date cannot be in the future."))

        if self.id_expiry_date and self.id_expiry_date < timezone.now().date():
            raise ValidationError(_("ID expiry date cannot be in the past."))

        if self.date_of_employment and self.date_of_employment > timezone.now().date():
            raise ValidationError(_("Date of employment cannot be in the future."))

        if self.id_expiry_date and self.id_expiry_date <= self.id_issue_date:
            raise ValidationError(_("ID expiry date must be after the ID issue date."))


    def save(self, *args, **kwargs):
        """
        Save the profile data.
        :param args:
        :param kwargs:
        :return: None
        """
        self.full_clean()
        super().save(*args, **kwargs)


    def is_complete_with_next_of_kin(self):
        """
        Check if the profile is complete with next of kin.
        :return: True if complete, False otherwise
        """
        required_fields = [
            self.gender,
            self.marital_status,
            self.phone_number,
            self.address,
            self.date_of_birth,
            self.identification_type,
            self.country_of_birth,
            self.place_of_birth,
            self.id_issue_date,
            self.id_expiry_date,
            self.employment_status,
            self.passport_number,
            self.nationality,
            self.city,
            self.employer_name,
            self.annual_income,
            self.date_of_employment,
            self.employer_address,
            self.employer_city,
            self.employer_state,
            self.photo,
            self.photo_url,
            self.id_photo,
            self.id_photo_url,
            self.signature_photo,
            self.signature_photo_url
        ]
        return  all(required_fields) and self.next_of_kin.exists()

    def __str__(self):
        return f"{self.gender} {self.marital_status} {self.phone_number}"



class NextOfKin(TimeStampedModel):
    """
    Next of kin model.
    """
    class RelationshipChoice(models.TextChoices):
        PARENT = ("Parent", _("Parent"))
        SIBLING = ("Sibling", _("Sibling"))
        CHILD = ("Child", _("Child"))
        FRIEND = ("Friend", _("Friend"))
        OTHER = ("Other", _("Other"))

    class SalutationChoice(models.TextChoices):
        MR = "mr", _("Mr.")
        MRS = "mrs", _("Mrs.")
        MS = "ms", _("Ms.")
        DR = "dr", _("Dr.")
        PROF = "prof", _("Prof.")
    class GenderChoice(models.TextChoices):
        MALE = ("Male", _("Male"))
        FEMALE = ("Female", _("Female"))

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="next_of_kin")

    title = models.CharField(_("Salutation"), choices=SalutationChoice.choices, default=SalutationChoice.MR, max_length=5)

    first_name = models.CharField(_("First Name"), max_length=100)

    last_name = models.CharField(_("Last Name"), max_length=100)

    other_name = models.CharField(_("Other Name"), max_length=100)

    date_of_birth = models.DateField(_("Date of birth"), blank=True, null=True)

    gender = models.CharField(_("Gender"), choices=GenderChoice.choices ,  max_length=10)

    email_address = models.EmailField(_("Email address"), max_length=100, blank=True, null=True, db_index=True)

    relationship = models.CharField(_("Relationship"), choices=RelationshipChoice.choices, max_length=10)

    phone_number = PhoneNumberField(_("Phone number"), max_length=15, blank=True, null=True)

    address = models.TextField(_("Address"), blank=True, null=True)

    city = models.CharField(_("City"), max_length=100, blank=True, null=True)

    state = models.CharField(_("State"), max_length=100, blank=True, null=True)

    country = CountryField(_("Country"), blank=True, null=True)

    is_primary = models.BooleanField(_("Is primary"), default=False)

    def clean(self):
        super().clean()
        if self.is_primary:
            primary = NextOfKin.objects.filter(
                profile=self.profile,
                is_primary=True
            ).exclude(pk=self.pk)
            if primary.exists():
                raise ValidationError(_("Only one next of kin can be marked as primary."))


    def save(self, *args, **kwargs):
        """
        Save the next of kin data.
        :param args:
        :param kwargs:
        :return: None
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} - {self.last_name} - Next of kin for {self.profile.user.full_name}"


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "is_primary"],
                name="unique_primary_next_of_kin",
                condition=models.Q(is_primary=True)
            )
        ]