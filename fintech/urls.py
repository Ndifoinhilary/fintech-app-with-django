from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/auth/", include("apps.account.urls")),
    path("api/v1/auth/", include("djoser.urls")),
    path(
        "api/v1/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

admin.site.site_header = _("Fintech Admin")
admin.site.site_title = _("Fintech Admin")
admin.site.index_title = _("Welcome to Fintech Admin")
