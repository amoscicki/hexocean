from django.urls import path, include
from rest_framework import routers
from .views import ImageViewSet, GenerateExpiringLinkViewSet
from django.conf.urls.static import static
from django.conf import settings

router = routers.DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'links', GenerateExpiringLinkViewSet)

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
