from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import  gettext as _
from loguru import logger


def send_otp_email(email, otp):
    """
    Send an OTP email to the user.
    :param email:
    :param otp:
    :return:
    """
    subject = _("OTP confirmation")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    context = {
        'otp': otp,
        'site_name': settings.SITE_NAME,
        'expires_time': settings.OTP_EXPIRATION_TIME,
    }
    template_name = 'emails/otp_email.html'
    html_message = render_to_string(template_name, context)
    plain_email = strip_tags(html_message)
    email = EmailMultiAlternatives(subject, plain_email, from_email, recipient_list)
    email.attach_alternative(html_message, "text/html")
    try:
        email.send()
        logger.success(_("OTP email sent"))
    except Exception as e:
        logger.error(_("Failed to send OTP email: {}").format(e))


def send_account_locked_email(self):
    """
    Send an account locked email to the user.
    :param self:
    :return:
    """
    subject = _("Account Locked")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [self.email]
    context = {
        'site_name': settings.SITE_NAME,
        'login_attempts_limit': settings.LOGIN_ATTEMPTS_LIMIT,
        'lockout_duration': int(settings.LOCKOUT_DURATION.total_seconds() // 60),
    }
    template_name = 'emails/account_locked.html'
    html_message = render_to_string(template_name, context)
    plain_email = strip_tags(html_message)
    email = EmailMultiAlternatives(subject, plain_email, from_email, recipient_list)
    email.attach_alternative(html_message, "text/html")
    try:
        email.send()
        logger.success(_("Account locked email sent"))
    except Exception as e:
        logger.error(_("Failed to send account locked email: {}").format(e))