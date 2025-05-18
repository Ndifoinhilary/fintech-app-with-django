from django.urls import path

from .views import CustomTokenCreatView, LogoutView, OTPVerifyView, CustomTokenRefreshView

urlpatterns = [
    path("login/", CustomTokenCreatView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify-otp/", OTPVerifyView.as_view(), name="verify_otp"),
    path("refresh-token/", CustomTokenRefreshView.as_view(), name="refresh_token"),
]
