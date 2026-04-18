from django.urls import path

from .views import (
    CommandHistoryAPIView,
    CommandParseAPIView,
    DashboardInsightsAPIView,
    DraftConfirmAPIView,
    DraftListAPIView,
    DraftPreviewAPIView,
    EditPreviousMessageAPIView,
    ResendLastMailAPIView,
    SentMailHistoryAPIView,
)

urlpatterns = [
    path('commands/parse/', CommandParseAPIView.as_view(), name='command-parse'),
    path('drafts/preview/', DraftPreviewAPIView.as_view(), name='draft-preview'),
    path('drafts/confirm/', DraftConfirmAPIView.as_view(), name='draft-confirm'),
    path('drafts/edit-previous/', EditPreviousMessageAPIView.as_view(), name='edit-previous'),
    path('drafts/', DraftListAPIView.as_view(), name='draft-list'),
    path('history/sent/', SentMailHistoryAPIView.as_view(), name='sent-history'),
    path('history/commands/', CommandHistoryAPIView.as_view(), name='command-history'),
    path('insights/dashboard/', DashboardInsightsAPIView.as_view(), name='dashboard-insights'),
    path('actions/resend-last/', ResendLastMailAPIView.as_view(), name='resend-last'),
]
