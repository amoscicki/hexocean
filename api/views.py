from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Image, Link
from .serializers import ImageSerializer, LinkSerializer
from .renderers import JPEGRenderer, PNGRenderer
from PIL import Image as PILImage


class ImageViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post']
    queryset = Image.objects.none()
    permission_classes = [IsAuthenticated]

    serializer_class = ImageSerializer

    def create(self, request, format=None):
        serializer = ImageSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, format=None):
        current_user = request.user
        images = Image.objects.filter(user=current_user)
        serializer = ImageSerializer(images, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class GenerateExpiringLinkViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','post']
    queryset = Link.objects.none()
    permission_classes = [IsAuthenticated]

    serializer_class = LinkSerializer
    
    def create(self, request, format=None):
        if not request.user.plan.expiring_link:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = LinkSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, format=None):
        current_user = request.user
        links = Link.objects.filter(image__user=current_user)
        serializer = LinkSerializer(links, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ExpiringLinkViewSet(generics.RetrieveAPIView):
    renderer_classes = [JPEGRenderer, PNGRenderer]
    
    def get(self, request, *args, **kwargs):
        queryset = Link.objects.get(id=kwargs['id'])
        if queryset.expires_at < timezone.now():
            return Response({'Expired': 'True'},status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, content_type='text/plain')
        
        image = queryset.image.image
        if image is None:
            return Response({'Not found': 'True'}, content_type='text/plain',status=status.HTTP_404_NOT_FOUND)
        
        format = PILImage.open(image).format
            
        if format == 'JPEG':
            return Response(image, content_type='image/jpeg', status=status.HTTP_200_OK)
        if format == 'PNG':
            return Response(image, content_type='image/png', status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_418_IM_A_TEAPOT)
