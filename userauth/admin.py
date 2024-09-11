from django.contrib import admin
from .models import CustomUser, PasswordReset, Otp


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "is_active",
        "is_admin",
        "is_superuser",
        "date_joined",
        "last_login_time",
        "last_logout_time",
    )
    search_fields = ("email", "username")
    list_filter = ("is_active", "is_superuser", "date_joined", "is_admin")
    ordering = ("-date_joined",)
    readonly_fields = (
        "last_login_time",
        "last_logout_time",
    )


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "expires_at")
    search_fields = ("user__email", "reset_token")
    list_filter = ("created_at", "expires_at")
    ordering = ("-created_at",)


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at", "expires_at")
    search_fields = ("user__email", "otp")
    list_filter = ("created_at", "expires_at")
    ordering = ("-created_at",)
