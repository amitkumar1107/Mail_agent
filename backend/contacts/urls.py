from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContactGroupViewSet, ContactViewSet

router = DefaultRouter()
router.register(r'groups', ContactGroupViewSet, basename='contact-group')
router.register(r'', ContactViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]
