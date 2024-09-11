from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, PasswordReset, Otp

# from django.utils import timezone


class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "confirm_password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True,
                "validators": [validate_password],
            },
        }

    def validate(self, data):
        # Check if passwords match
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Check if email is already registered
        if CustomUser.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email is already registered."})

        # Check if username is already taken
        if CustomUser.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError(
                {"username": "Username is already taken."}
            )

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )

    class Meta:
        model = CustomUser
        fields = ["email", "password"]


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        user = CustomUser.objects.get(email=email)

        password_reset, created = PasswordReset.objects.get_or_create(user=user)

        success = password_reset.initiate_password_reset()
        if not success:
            raise serializers.ValidationError("Failed to send OTP. Please try again.")

        return password_reset


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return data

    def save(self, **kwargs):
        email = self.context.get("email")
        if not email:
            raise serializers.ValidationError("Email must be provided.")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

        return user


class OtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=4, required=True)

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        try:
            otp_verification = Otp.objects.get(user=user)
        except Otp.DoesNotExist:
            raise serializers.ValidationError({"otp": "OTP record not found."})

        if not otp_verification.verify_otp(otp):
            raise serializers.ValidationError(
                {"otp": "Invalid OTP or OTP has expired."}
            )

        data["user"] = user
        return data

    def create(self, validated_data):
        return validated_data
