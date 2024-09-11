from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from .otp_utils import generate_and_send_otp, generate_otp
from .managers import CustomUserManager
from datetime import timedelta


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True, verbose_name="Email", max_length=255)
    username = models.CharField(max_length=150, unique=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    last_logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username or self.email.split("@")[0]

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def save(self, *args, **kwargs):
        if self.pk:  # Check if the instance already exists
            if self.is_active and not self.last_login_time:
                self.last_login_time = timezone.now()
            elif not self.is_active and not self.last_logout_time:
                self.last_logout_time = timezone.now()
        super().save(*args, **kwargs)


class PasswordReset(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="password_reset"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.email

    def initiate_password_reset(self):
        """Generate an OTP and initiate the password reset process."""
        otp_instance = Otp.create_and_save_otp(self.user)
        return otp_instance


class Otp(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="otp_verification"
    )
    otp = models.CharField(max_length=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @classmethod
    def create_and_save_otp(cls, user):
        """Create and save OTP for the given user."""
        otp_code = generate_otp()
        otp_instance, created = cls.objects.update_or_create(
            user=user,
            defaults={
                "otp": otp_code,
                "created_at": timezone.now(),
                "expires_at": timezone.now() + timedelta(minutes=5),
            },
        )
        generate_and_send_otp(otp_instance)
        return otp_instance

    def verify_otp(self, otp):
        """Verify the provided OTP."""
        return self.otp == otp and timezone.now() < self.expires_at

    def resend_otp(self):
        """Resend OTP using utility function."""
        return generate_and_send_otp(self)
