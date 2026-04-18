from rest_framework import permissions, viewsets

from .models import Contact, ContactGroup
from .serializers import ContactGroupSerializer, ContactSerializer


class ContactGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContactGroup.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Contact.objects.filter(user=self.request.user).select_related('group')

        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(full_name__icontains=search)

        relationship = self.request.query_params.get('relationship', '').strip()
        if relationship:
            queryset = queryset.filter(relationship=relationship)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
