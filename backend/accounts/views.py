import logging
import random
import smtplib
from datetime import timedelta

from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailOTP
from .serializers import (
    LoginSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    SignUpSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class EmailSendException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Unable to send verification email. Please try again later.'
    default_code = 'email_send_failed'

OTP_EXPIRY_MINUTES = 10


def _generate_otp_code() -> str:
    return f'{random.randint(0, 999999):06d}'


def _create_and_send_otp(user: User) -> EmailOTP:
    EmailOTP.objects.filter(
        user=user,
        purpose=EmailOTP.PURPOSE_EMAIL_VERIFICATION,
        is_used=False,
    ).update(is_used=True)

    otp = EmailOTP.objects.create(
        user=user,
        code=_generate_otp_code(),
        purpose=EmailOTP.PURPOSE_EMAIL_VERIFICATION,
        expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )

    try:
        send_mail(
            subject='Your verification OTP',
            message=f'Your OTP is {otp.code}. It is valid for {OTP_EXPIRY_MINUTES} minutes.',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except (smtplib.SMTPException, OSError) as exc:
        logger.exception('Failed to send verification OTP for user %s', user.pk)
        raise EmailSendException() from exc

    return otp


def _build_jwt_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SignUpAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth'

    def post(self, request):
        print("Received signup request with data:", request.data)
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
            print("Created user:", user)
            _create_and_send_otp(user)
        return Response(
            {
                'message': 'Account created. Please verify your email with OTP.',
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'auth'

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response(
                {'detail': 'Email not verified. Please verify OTP first.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = _build_jwt_tokens(user)
        return Response(
            {
                'message': 'Login successful.',
                'user': UserSerializer(user).data,
                'tokens': tokens,
            }
        )


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = 'auth'

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful.'})


class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'user': UserSerializer(request.user).data})


class RequestEmailOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower().strip()
        user = User.objects.filter(email__iexact=email).first()
        if user is not None:
            try:
                _create_and_send_otp(user)
            except EmailSendException as exc:
                logger.exception('Failed to resend OTP for existing user %s', user.pk)
                return Response({'detail': str(exc.detail)}, status=exc.status_code)

        # Generic response avoids account/email enumeration.
        return Response({'message': 'If this email exists, an OTP has been sent.'})


class VerifyEmailOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower().strip()
        code = serializer.validated_data['code']

        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        otp = EmailOTP.objects.filter(
            user=user,
            purpose=EmailOTP.PURPOSE_EMAIL_VERIFICATION,
            code=code,
            is_used=False,
        ).order_by('-created_at').first()

        if otp is None:
            return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp.expires_at < timezone.now():
            return Response({'detail': 'OTP expired. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save(update_fields=['is_used'])

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])

        return Response({'message': 'Email verified successfully.'})
