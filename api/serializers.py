import datetime
from rest_framework import serializers
from .models import Image, Link
from .utils import generate_thumbnail

class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'image')
        extra_kwargs = {
            'user': {'read_only': True},
            'height': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        thumbnail_sizes = user.plan.thumbnail_sizes.all()
        image = validated_data['image']
        
        if image.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError(f'Image must be jpg or png')

        images = []

        for size in thumbnail_sizes:
            thumbnail = generate_thumbnail(image, size.height)
            images.append(Image(user=user, image=thumbnail, height=size.height))
        if user.plan.original_available:
            images.append(Image(user=user, image=image, height=0))
        for image in images:
            image.save()

        return images
    
    def to_representation(self, instance):
        request = self.context['request']
        representation = dict()
        if isinstance(instance, list):
            for image in instance:
                if image.height == 0:
                    representation[f'original'] = request.build_absolute_uri(image.image.url)
                else:
                    key = f'thumbnail_{image.height}'
                    representation[key] = request.build_absolute_uri(image.image.url)
            
            return representation
        representation['image_link'] = request.build_absolute_uri(instance.image.url)
        return representation
    
class LinkSerializer(serializers.ModelSerializer):

    valid_for = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Link
        fields = ['image', 'valid_for']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'expires_at': {'read_only': True},
        }

    def create(self, validated_data):
        
        valid_for = validated_data['valid_for']
        if not 300 <= valid_for <= 30000:
            raise serializers.ValidationError('Valid for must be between 300 and 30000 seconds')
        
        image = validated_data['image']
        created_at = datetime.datetime.now()
        expires_at = created_at + datetime.timedelta(seconds=valid_for)
        return Link.objects.create(image=image, created_at=created_at, expires_at=expires_at)
    
    def to_representation(self, instance):
        request = self.context['request']
        representation = dict()
        representation['link'] = request.build_absolute_uri(f'/templink/{instance.id}')
        representation['expires_at'] = instance.expires_at.strftime('%Y-%m-%d %H:%M:%S')
        representation['related_image'] = request.build_absolute_uri(instance.image.image.url)
        return representation
        