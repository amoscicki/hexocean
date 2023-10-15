from io import BytesIO
from PIL import Image as PILImage
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers
import base64
import hashlib
import hmac
import time

def generate_thumbnail(image, height):
    # resize image to thumbnail, using format from original image
    img = PILImage.open(image)
    width = int(img.width * height / img.height)
    img.thumbnail((width, height))
    buffer = BytesIO()
    thumbnail = None
    
    if img.format == 'JPEG':
        img.save(buffer, format='JPEG')
        thumbnail = InMemoryUploadedFile(buffer, None, f'{image.name.split(".")[0]}_{height}.jpg', 'image/jpeg', buffer.getbuffer().nbytes, None)
        thumbnail.name = f'{image.name.split(".")[0]}_{height}.jpg'
        thumbnail.url = f'{settings.MEDIA_URL}{thumbnail.name}'

    if img.format == 'PNG':
        img.save(buffer, format='PNG')
        thumbnail = InMemoryUploadedFile(buffer, None, f'{image.name.split(".")[0]}_{height}.png', 'image/png', buffer.getbuffer().nbytes, None)
        thumbnail.name = f'{image.name.split(".")[0]}_{height}.png'
        thumbnail.url = f'{settings.MEDIA_URL}{thumbnail.name}'
        
    return thumbnail
