from rest_framework import serializers


class VoiceTranscribeSerializer(serializers.Serializer):
    audio = serializers.FileField()
    route_to_parser = serializers.BooleanField(required=False, default=True)


class VoiceConfirmSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True, default='Do you want to send this email?')
