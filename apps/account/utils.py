import string


def generate_otp(length: int = 6) -> str:
    """
    Generate a one-time password (OTP) of a given length.
    The OTP is a string of digits.

    Args:
        length (int): Length of the OTP. Default is 6.

    Returns:
        str: Generated OTP.
    """
    import random

    return ''.join(random.choices(string.digits, k=length))
