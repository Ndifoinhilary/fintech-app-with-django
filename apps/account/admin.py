from cloudinary.forms import CloudinaryFileField
from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import UserCreationForm, UserChangeForm
from .models import Profile,NextOfKin

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



class ProfileAdminForm(forms.ModelForm):
    photo = CloudinaryFileField( options={"crop":"thumb", "width":200, "height":200, "folder":"fintech_profile"} )
    class Meta:
        model = Profile
        fields = "__all__"



class NextOfKinInline(admin.TabularInline):
    """
    Inline admin for NextOfKin model to display in Profile admin.
    """
    model = NextOfKin
    extra = 1
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'first_name', 'last_name', 'other_name', 'is_primary')
        }),
        (_('Personal Details'), {
            'fields': ('date_of_birth', 'gender', 'relationship')
        }),
        (_('Contact Information'), {
            'fields': ('email_address', 'phone_number', 'address', 'city', 'state', 'country')
        }),
    )
    readonly_fields = ('created', 'modified')


class ProfileCompletionFilter(SimpleListFilter):
    """Filter profiles by completion status."""
    title = _('Profile Completion')
    parameter_name = 'completion'

    def lookups(self, request, model_admin):
        return (
            ('complete', _('Complete with Next of Kin')),
            ('incomplete', _('Incomplete')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'complete':
            return queryset.filter(next_of_kin__isnull=False).distinct()
        if self.value() == 'incomplete':
            # This is a simplification - actual implementation would call is_complete_with_next_of_kin
            # on each profile which would be inefficient for large datasets
            return queryset.filter(next_of_kin__isnull=True)


class EmploymentStatusFilter(SimpleListFilter):
    """Filter profiles by employment status."""
    title = _('Employment Status')
    parameter_name = 'employment_status'

    def lookups(self, request, model_admin):
        return Profile.EmploymentChoice.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(employment_status=self.value())


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin for Profile model.
    """
    form = ProfileAdminForm
    list_display = ('user', 'display_name', 'phone_number', 'employment_status',
                    'nationality', 'profile_completion', 'has_next_of_kin', 'view_user_link')
    list_filter = ('gender', 'marital_status', EmploymentStatusFilter,
                   'nationality', 'employment_status', ProfileCompletionFilter)
    search_fields = ('user__email', 'user__first_name', 'user__last_name',
                     'phone_number', 'passport_number', 'city')
    readonly_fields = ('created', 'modified', 'display_photos')
    inlines = [NextOfKinInline]

    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'title')
        }),
        (_('Personal Information'), {
            'fields': ('gender', 'marital_status', 'date_of_birth', 'place_of_birth',
                       'country_of_birth', 'nationality')
        }),
        (_('Contact Information'), {
            'fields': ('phone_number', 'address', 'city')
        }),
        (_('Identification'), {
            'fields': ('identification_type', 'passport_number',
                       'id_issue_date', 'id_expiry_date')
        }),
        (_('Employment Information'), {
            'fields': ('employment_status', 'employer_name', 'annual_income',
                       'date_of_employment', 'employer_address', 'employer_city', 'employer_state')
        }),
        (_('Photos'), {
            'fields': ('display_photos',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def display_name(self, obj):
        """Display the user's full name."""
        return obj.user.get_full_name() if hasattr(obj.user, 'get_full_name') else obj.user.username

    display_name.short_description = _('Name')

    def has_next_of_kin(self, obj):
        """Check if the profile has next of kin."""
        return obj.next_of_kin.exists()

    has_next_of_kin.boolean = True
    has_next_of_kin.short_description = _('Has Next of Kin')

    def profile_completion(self, obj):
        """Display profile completion status."""
        return obj.is_complete_with_next_of_kin()

    profile_completion.boolean = True
    profile_completion.short_description = _('Profile Complete')

    def view_user_link(self, obj):
        """Create a link to the user admin."""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, _('View User'))

    view_user_link.short_description = _('User Details')

    def display_photos(self, obj):
        """Display profile photos in the admin."""
        html = ""
        if obj.photo_url:
            html += format_html('<p><strong>Profile Photo:</strong><br/><img src="{}" width="200"/></p>', obj.photo_url)
        if obj.id_photo_url:
            html += format_html('<p><strong>ID Photo:</strong><br/><img src="{}" width="200"/></p>', obj.id_photo_url)
        if obj.signature_photo_url:
            html += format_html('<p><strong>Signature:</strong><br/><img src="{}" width="200"/></p>',
                                obj.signature_photo_url)
        return html or _("No photos available")

    display_photos.short_description = _('Profile Photos')


@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):
    """
    Admin for NextOfKin model.
    """
    list_display = ('full_name', 'relationship', 'profile_user', 'phone_number', 'is_primary')
    list_filter = ('relationship', 'gender', 'is_primary')
    search_fields = ('first_name', 'last_name', 'other_name', 'phone_number',
                     'profile__user__email', 'profile__user__first_name', 'profile__user__last_name')
    readonly_fields = ('created', 'modified')

    fieldsets = (
        (_('Profile'), {
            'fields': ('profile', 'is_primary')
        }),
        (_('Personal Information'), {
            'fields': ('title', 'first_name', 'last_name', 'other_name',
                       'date_of_birth', 'gender', 'relationship')
        }),
        (_('Contact Information'), {
            'fields': ('email_address', 'phone_number', 'address', 'city', 'state', 'country')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile__user')

    def full_name(self, obj):
        """Display the next of kin's full name."""
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = _('Full Name')

    def profile_user(self, obj):
        """Display the profile's user."""
        user_url = reverse('admin:auth_user_change', args=[obj.profile.user.id])
        profile_url = reverse('admin:app_profile_change', args=[obj.profile.id])
        return format_html(
            '<a href="{}">{}</a> (<a href="{}">{}</a>)',
            user_url, obj.profile.user.get_full_name() if hasattr(obj.profile.user,
                                                                  'get_full_name') else obj.profile.user.username,
            profile_url, _('View Profile')
        )

    profile_user.short_description = _('User')