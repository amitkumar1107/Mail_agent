from rest_framework import serializers

from .models import EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = (
            'id',
            'name',
            'category',
            'intent_key',
            'subject_template',
            'body_template',
            'is_system',
            'is_active',
            'usage_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'is_system', 'usage_count', 'created_at', 'updated_at')


class TemplateRewriteSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    command_text = serializers.CharField(required=False, allow_blank=True, default='')
    tone = serializers.CharField(required=False, allow_blank=True, default='neutral')
    recipient_name = serializers.CharField(required=False, allow_blank=True, default='')
    relationship = serializers.CharField(required=False, allow_blank=True, default='other')


class TemplateSuggestionSerializer(serializers.Serializer):
    intent = serializers.CharField(required=False, allow_blank=True, default='general')
    category = serializers.CharField(required=False, allow_blank=True, default='')
