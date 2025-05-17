from django.conf import settings
from loguru import logger
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError


class CookieAuthentication(JWTAuthentication):
    """
    Custom authentication class that uses cookies to store the JWT token.
    """

    def authenticate(self, request):
        """
        Authenticate the user using the JWT token stored in cookies.
        """
        header = self.get_header(request)
        raw_token = None
        if header is not None:
            raw_token = self.get_raw_token(header)
        elif settings.COOKIE_NAME in request.COOKIES:
            # Check for the token in the cookie
            raw_token = request.COOKIES.get(settings.COOKIE_NAME)

        if raw_token is not None:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except TokenError as e:
                logger.error(f"Token error: {e}")
        return None
