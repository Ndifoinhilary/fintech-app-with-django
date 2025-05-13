from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import gettext_lazy as _

from .models import ContentView


# Register your models here.


@admin.register(ContentView)
class ContentViewAdmin(admin.ModelAdmin):
    """
    Admin interface for ContentView model.
    """
    list_display = ('content_type', 'object_id', 'user', 'ip_address', 'last_viewed', 'created_at', 'updated_at',)
    search_fields = ('content_type__model', 'object_id', 'ip_address',)
    list_filter = ('content_type', 'user', 'ip_address',)
    date_hierarchy = 'last_viewed'
    readonly_fields = ['content_type', 'object_id', 'user', 'ip_address', 'last_viewed', 'created_at', 'updated_at']
    ordering = ('-last_viewed',)

    fieldsets = (
        (None, {
            'fields': ('content_type', 'object_id', 'content_object',)
        }),
        (_('User Information'), {
            'fields': ('user', 'ip_address',)
        }),
        (_('View Information'), {
            'fields': ('last_viewed',)
        }),
        (_('Timestamps'),
         {'fields': ('created_at', 'updated_at',), 'classes': ('collapse',)}
         ),
    )

    def has_add_permission(self, request):
        """
        Disable the add permission for ContentView.
        :param request: The request object.
        :return: False
        """
        return False
    def has_change_permission(self, request, obj=None):
        """
        Disable the change permission for ContentView.
        :param request:
        :param obj:
        :return: False
        """
        return False

class ContentViewInline(GenericTabularInline):
    """
    Inline admin interface for ContentView model.
    """
    model = ContentView
    extra = 0
    fields = ('user', 'ip_address', 'last_viewed', 'created_at', 'updated_at',)
    readonly_fields = ('content_type', 'object_id', 'user', 'ip_address', 'last_viewed',)
    can_delete = False

    def has_add_permission(self, request) -> bool:
        """
        Disable the add permission for ContentView.
        :param request: The request object.
        :return: False
        """
        return False