from http import HTTPStatus
from typing import Optional

from django.conf import settings
from django.utils import timezone
from djoser.views import TokenCreateView, User
from loguru import logger
from rest_framework import serializers, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .helpers.emails import send_otp_email
from .utils import generate_otp


def set_auth_cookie(response: Response, access_token: str, refresh_token: Optional[str] = None) -> None:
    """
    Set authentication cookies in the response.
    :param response: The HTTP response object.
    :param access_token: The access token to be set in the cookie.
    :param refresh_token: The refresh token to be set in the cookie.
    """
    access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    # Set the access and refresh tokens in cookies
    cookie_settings = {
        'path': settings.COOKIE_PATH,
        'httponly': settings.COOKIE_HTTPONLY,
        'samesite': settings.COOKIE_SAMESITE,
        'secure': settings.SECURE_COOKIES,
        'max_age': access_token_lifetime,
    }
    response.set_cookie(settings.COOKIE_NAME, access_token, **cookie_settings)
    if refresh_token:
        cookie_settings['max_age'] = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        response.set_cookie('refresh_token', refresh_token, **cookie_settings)

    logged_in_cookie_settings = cookie_settings.copy()
    logged_in_cookie_settings['httponly'] = False
    response.set_cookie("logged_in", "true", **logged_in_cookie_settings)


class CustomTokenCreatView(TokenCreateView):
    """
    Custom token create view to set cookies for access and refresh tokens.
    """

    def _action(self, serializer):
        """
        Override the action method to set cookies for access and refresh tokens.
        :param serializer: The serializer instance.
        :return: The HTTP response object.
        """
        user = serializer.user
        if user.is_locked_out:
            return Response({
                "detail": f"Account is locked  due to multiple attempts try again after {settings.LOCKOUT_DURATION.to_seconds() / 60} minutes."},
                status=HTTPStatus.FORBIDDEN)

        user.reset_failed_login_attempt()
        otp = generate_otp()
        user.set_otp(otp)
        send_otp_email(user.email, otp)
        logger.info(f"OTP sent to {user.email}: {otp}")
        return Response({
            "detail": "OTP sent to your email. Please verify to log in."
        }, status=HTTPStatus.OK)

    def post(self, request, *args, **kwargs):
        """
        Override the post method to handle the OTP verification.
        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response object.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return self._action(serializer)
        except serializers.ValidationError as e:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                locked_user = user.handle_failed_login_attempt()
                if locked_user:
                    return Response({
                        "detail": "Account is temporarily locked due to multiple failed login attempts."},
                        status=HTTPStatus.FORBIDDEN)
            logger.error(f"Failed login attempt for {email}")
            return Response({"detail": "Invalid credentials provided."}, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return Response({"detail": "An unexpected error occurred. Please try again later."},
                            status=HTTPStatus.INTERNAL_SERVER_ERROR)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view to set cookies for access and refresh tokens.
    """

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Override the post method to set cookies for access and refresh tokens.
        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response object.
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            logger.error(f"No refresh token provided for {request.path}")
            return Response({"detail": "Refresh token not found."}, status=HTTPStatus.UNAUTHORIZED)
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == HTTPStatus.OK:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            if access_token and refresh_token:
                set_auth_cookie(response, access_token, refresh_token)
                response.data.pop('refresh', None)
                response.data.pop('access', None)
                response.data['message'] = "Tokens refreshed successfully."
            else:
                response.data['message'] = 'Access or refresh token not found in response.'
                logger.error(f"Failed to retrieve tokens from response: {response.data}")
        return response


class OTPVerifyView(APIView):
    """
    APi view to verify the OTP sent to the user.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Verify the OTP sent to the user.
        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response object.
        """
        email = request.data.get('email')
        otp = request.data.get('otp')
        if not otp:
            return Response({"detail": "OTP is required."}, status=HTTPStatus.BAD_REQUEST)
        user = User.objects.filter(otp=otp, otp_expiry__gt=timezone.now()).first()
        if not user:
            return Response({"detail": "Invalid or expired OTP."}, status=HTTPStatus.BAD_REQUEST)

        if user.is_locked_out:
            return Response({
                "detail": f"Account is locked due to multiple attempts. Try again after {settings.LOCKOUT_DURATION.to_seconds() / 60} minutes."},
                status=HTTPStatus.FORBIDDEN)
        user.verify_otp(otp)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = Response({
            "detail": "OTP verified successfully.",
            "access": access_token,
            "refresh": refresh_token
        }, status=HTTPStatus.OK)
        set_auth_cookie(response, access_token, refresh_token)
        return response


class LogoutView(APIView):
    """
    API view to handle user logout.
    """
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle user logout.
        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response object.
        """
        response = Response({"detail": "Logged out successfully."}, status=HTTPStatus.OK)
        response.delete_cookie(settings.COOKIE_NAME)
        response.delete_cookie('refresh_token')
        response.delete_cookie('logged_in')
        return response