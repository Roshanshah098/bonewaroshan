import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    """Utility function to generate a 4-digit OTP."""
    return str(random.randint(1000, 9999))


def send_otp_to_user(user, otp):
    """Utility function to send an OTP via email."""
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}. It is valid for 5 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        print(f"OTP sent to email: {user.email}")
    except Exception as e:
        print(f"Failed to send OTP to {user.email}: {e}")


def generate_and_send_otp(otp_instance):
    """Generate a 4-digit OTP, save it to the OTP instance, and send it via email."""
    otp = generate_otp()
    send_otp_to_user(otp_instance.user, otp)

    # Save OTP and expiration to OTP instance
    try:
        otp_instance.otp = otp
        otp_instance.expires_at = timezone.now() + timedelta(minutes=5)
        otp_instance.save()
    except Exception as e:
        print(f"Error saving OTP to OTP instance: {e}")
        return False

    return True
