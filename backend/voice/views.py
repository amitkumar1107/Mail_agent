import os
import re
import tempfile

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from mail_core.ai import infer_command

from .serializers import VoiceConfirmSerializer, VoiceTranscribeSerializer


def _detect_language(text: str):
    lowered = text.lower().strip()
    if not lowered:
        return 'unknown'

    has_devanagari = any('\u0900' <= ch <= '\u097f' for ch in text)
    hindi_markers = ['hai', 'nahi', 'kya', 'ko', 'bhejo', 'yaar', 'kal', 'aaj']
    marker_hits = sum(1 for token in hindi_markers if token in lowered)
    has_english = any('a' <= ch <= 'z' for ch in lowered)

    if has_devanagari and has_english:
        return 'hinglish'
    if has_devanagari:
        return 'hindi'
    if marker_hits >= 2 and has_english:
        return 'hinglish'
    return 'english'


def _normalize_transcript(text: str) -> str:
    if not text:
        return ''

    cleaned = text.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'([!?.,])\1+', r'\1', cleaned)
    cleaned = re.sub(r'\b(um+|uh+|hmm+)\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def _transcribe_with_whisper(audio_path: str):
    try:
        import whisper  # type: ignore
    except Exception as exc:
        return None, f'Whisper is not installed: {exc}'

    model_name = os.getenv('WHISPER_MODEL', 'base')
    try:
        model = whisper.load_model(model_name)
    except Exception as exc:
        return None, f'Failed to load Whisper model {model_name}: {exc}'

    attempts = [
        {'fp16': False, 'temperature': 0.0},
        {'fp16': False, 'temperature': 0.2, 'condition_on_previous_text': False},
    ]

    last_error = ''
    for kwargs in attempts:
        try:
            result = model.transcribe(audio_path, **kwargs)
            text = _normalize_transcript((result or {}).get('text', ''))
            if text:
                return text, ''
        except Exception as exc:
            last_error = str(exc)

    if not last_error:
        last_error = 'Whisper returned empty transcript. Audio may be too noisy or too short.'
    return None, last_error


class VoiceTranscribeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VoiceTranscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        audio_file = serializer.validated_data['audio']
        route_to_parser = serializer.validated_data.get('route_to_parser', True)

        suffix = os.path.splitext(audio_file.name)[1] or '.wav'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            text, error = _transcribe_with_whisper(tmp_path)
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        if not text:
            return Response(
                {
                    'detail': 'Failed to transcribe audio.',
                    'error': error,
                    'hint': 'Install whisper model and ffmpeg in deployment environment.',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        language = _detect_language(text)
        payload = {
            'transcript': text,
            'language': language,
        }

        if route_to_parser:
            parsed = infer_command(text)
            payload['parsed'] = {
                'intent': parsed.get('intent', 'general'),
                'tone': parsed.get('tone', 'neutral'),
                'occasion': parsed.get('occasion', ''),
                'action': parsed.get('action', 'draft'),
                'schedule_time': parsed.get('schedule_time', ''),
                'recipient_name': parsed.get('recipient_name', ''),
                'ai_used': parsed.get('ai_used', False),
                'ai_error': parsed.get('ai_error', ''),
            }

        return Response(payload)


class VoiceConfirmAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VoiceConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data['text']

        return Response({'confirmation_text': text})
