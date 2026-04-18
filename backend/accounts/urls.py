from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    RequestEmailOTPAPIView,
    SignUpAPIView,
    VerifyEmailOTPAPIView,
)

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('me/', MeAPIView.as_view(), name='me'),
    path('otp/request/', RequestEmailOTPAPIView.as_view(), name='otp-request'),
    path('otp/verify/', VerifyEmailOTPAPIView.as_view(), name='otp-verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
