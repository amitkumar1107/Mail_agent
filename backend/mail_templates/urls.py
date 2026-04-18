from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EmailTemplateViewSet, TemplateRewriteAPIView

router = DefaultRouter()
router.register(r'', EmailTemplateViewSet, basename='email-template')

urlpatterns = [
    path('rewrite/', TemplateRewriteAPIView.as_view(), name='template-rewrite'),
    path('', include(router.urls)),
]
