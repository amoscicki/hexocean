from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Image, Link
from .serializers import ImageSerializer, LinkSerializer
from rest_framework.permissions import IsAuthenticated


class ImageViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post']
    queryset = Image.objects.none()
    permission_classes = [IsAuthenticated]

    serializer_class = ImageSerializer

    def create(self, request, format=None):
        current_user = request.user
        serializer = ImageSerializer(data=request.data, context={'user': current_user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, format=None):
        current_user = request.user
        images = Image.objects.filter(user=current_user)
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GenerateExpiringLinkViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','post']
    queryset = Link.objects.none()
    permission_classes = [IsAuthenticated]

    serializer_class = LinkSerializer
    
    def create(self, request, format=None):
        serializer = LinkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, format=None):
        current_user = request.user
        links = Link.objects.filter(image__user=current_user)
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
