from django.urls import path

from .views import VoiceConfirmAPIView, VoiceTranscribeAPIView

urlpatterns = [
    path('transcribe/', VoiceTranscribeAPIView.as_view(), name='voice-transcribe'),
    path('confirm/', VoiceConfirmAPIView.as_view(), name='voice-confirm'),
]
