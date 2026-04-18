from django.db.models import Q
from rest_framework import serializers

from .models import Contact, ContactGroup


class ContactGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactGroup
        fields = ('id', 'name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ContactSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id',
            'group',
            'group_name',
            'full_name',
            'email',
            'phone',
            'relationship',
            'birth_date',
            'anniversary_date',
            'tags',
            'notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'group_name')

    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Tags must be a list of strings.')

        cleaned = []
        for tag in value:
            if not isinstance(tag, str):
                raise serializers.ValidationError('Each tag must be a string.')
            tag_clean = tag.strip()
            if tag_clean:
                cleaned.append(tag_clean)

        deduped = list(dict.fromkeys(cleaned))
        return deduped

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        email = (attrs.get('email') or '').strip().lower()
        phone = (attrs.get('phone') or '').strip()

        attrs['email'] = email
        attrs['phone'] = phone

        if not email and not phone:
            raise serializers.ValidationError('At least one of email or phone is required.')

        queryset = Contact.objects.filter(user=user)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        duplicate_query = Q()
        if email:
            duplicate_query |= Q(email__iexact=email)
        if phone:
            duplicate_query |= Q(phone=phone)

        if duplicate_query and queryset.filter(duplicate_query).exists():
            raise serializers.ValidationError('Duplicate contact detected with same email or phone.')

        group = attrs.get('group')
        if group and group.user_id != user.id:
            raise serializers.ValidationError('Selected group does not belong to current user.')

        return attrs
