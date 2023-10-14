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
        user = self.context['user']
        thumbnail_sizes = user.plan.thumbnail_sizes.all()
        image = validated_data['image']
        
        # check if image is jpg or png
        if image.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError('Image must be jpg or png')

        images = []
        for size in thumbnail_sizes:
            thumbnail = generate_thumbnail(image, size.height)
            images.append(Image(user=user, image=thumbnail, height=size.height))
        if user.plan.original_available:
            images.append(Image(user=user, image=image, height=0))
        for image in images:
            image.save()

        return images
    
    # override to_representation to return created images addresses
    def to_representation(self, instance):
        if isinstance(instance, list):
            representation = dict()
            for image in instance:
                if image.height == 0:
                    representation[f'original'] = image.image
                else:
                    key = f'thumbnail_{image.height}'
                    representation[key] = image.image
            
            return representation
        return super().to_representation(instance)

class LinkSerializer(serializers.ModelSerializer):

    valid_for = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Link
        fields = ['image', 'valid_for']
        extra_kwargs = {
            'link': {'read_only': True},
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
        link = f'{image.image.url}/{datetime.datetime.now().timestamp()}'
        return Link.objects.create(image=image, created_at=created_at, expires_at=expires_at, link=link)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['link'] = request.build_absolute_uri(instance.link)
        return representation
        