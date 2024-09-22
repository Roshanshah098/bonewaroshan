from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

# from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

from .models import CustomUser, PasswordReset, Otp
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    OtpSerializer,
    PasswordResetConfirmSerializer,
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token = get_tokens_for_user(user)
            response_data = {
                "token": token,
                "detail": "User registered successfully.",
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(email=email, password=password)

            if user is not None and user.is_active:
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
                token = get_tokens_for_user(user)
                return Response(
                    {
                        "token": token,
                        "detail": "Login successful.",
                    },
                    status=status.HTTP_200_OK,
                ) 
            return Response(
                {"detail": "Invalid credentials or inactive account."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            password_reset = serializer.save()  # This sends OTP
            user = CustomUser.objects.get(email=request.data["email"])
            tokens = get_tokens_for_user(user)

            return Response(
                {
                    "detail": "OTP sent to your email.",
                    "refresh": tokens["refresh"],
                    "access": tokens["access"],
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        # Extract email from query params or request data if needed
        email = request.data.get("email")

        # Ensure email is provided
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Pass email to serializer context
        serializer = self.get_serializer(data=request.data, context={"email": email})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()  # This updates the password
            tokens = get_tokens_for_user(user)

            return Response(
                {
                    "detail": "Password reset successfully.",
                    "refresh": tokens["refresh"],
                    "access": tokens["access"],
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            # Clean up OTP after successful verification
            # Otp.objects.filter(user=user).delete()

            return Response(
                {
                    "detail": "OTP verified successfully.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "OTP verification record not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
