from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserCreationForm, UserChangeForm

# Register your models here.
User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ["email", "username", "first_name", "last_name", "is_staff", "is_active", "role"]
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (_("Login Credentials"), {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "middle_name", "last_name", "role", "id_no")}),
        (_("Account Status"), {"fields": ("account_status", "last_login_attempt", "failed_login_attempts",)}),
        (_("Security"), {"fields": ("security_question", "security_answer")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("date_joined", "last_login")}),
    )
    search_fields = ("email", "username", "first_name", "last_name", "id_no")
    ordering = ("email",)
