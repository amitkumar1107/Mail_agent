from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from mail_core.ai import generate_email

from .models import EmailTemplate
from .serializers import EmailTemplateSerializer, TemplateRewriteSerializer, TemplateSuggestionSerializer


class EmailTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_templates = EmailTemplate.objects.filter(user=self.request.user, is_active=True)
        system_templates = EmailTemplate.objects.filter(is_system=True, is_active=True)
        return (user_templates | system_templates).distinct().order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_system=False)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.is_system:
            raise PermissionDenied('System templates cannot be edited.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_system:
            raise PermissionDenied('System templates cannot be deleted.')
        instance.delete()

    @action(detail=False, methods=['get'], url_path='suggest')
    def suggest(self, request):
        params = TemplateSuggestionSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        intent = params.validated_data.get('intent', 'general')
        category = params.validated_data.get('category', '')

        user_templates = EmailTemplate.objects.filter(user=request.user, is_active=True)
        system_templates = EmailTemplate.objects.filter(is_system=True, is_active=True)
        queryset = (user_templates | system_templates).distinct()

        if intent:
            queryset = queryset.filter(intent_key__in=[intent, 'general'])
        if category:
            queryset = queryset.filter(category=category)

        queryset = queryset.order_by('-usage_count', 'name')[:10]
        return Response({'results': EmailTemplateSerializer(queryset, many=True).data})


class TemplateRewriteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TemplateRewriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template_id = serializer.validated_data['template_id']
        command_text = serializer.validated_data.get('command_text', '')
        tone = serializer.validated_data.get('tone', 'neutral')
        recipient_name = serializer.validated_data.get('recipient_name', '')
        relationship = serializer.validated_data.get('relationship', 'other')

        template = (
            EmailTemplate.objects.filter(id=template_id, user=request.user)
            | EmailTemplate.objects.filter(id=template_id, is_system=True)
        ).first()
        if template is None:
            return Response({'detail': 'Template not found.'}, status=status.HTTP_404_NOT_FOUND)

        intent = template.intent_key or 'general'
        seed_command = command_text or template.body_template
        generated = generate_email(
            command_text=seed_command,
            intent=intent,
            tone=tone,
            recipient_name=recipient_name,
            relationship=relationship,
        )

        if generated.get('subject') and generated.get('body'):
            subject = generated['subject']
            body = generated['body']
            ai_used = generated.get('ai_used', False)
        else:
            subject = template.subject_template
            body = template.body_template
            ai_used = False

        template.usage_count += 1
        template.save(update_fields=['usage_count'])

        return Response(
            {
                'template': EmailTemplateSerializer(template).data,
                'subject': subject,
                'body': body,
                'ai_used': ai_used,
                'ai_error': generated.get('ai_error', ''),
            }
        )
