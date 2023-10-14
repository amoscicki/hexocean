from io import BytesIO
from PIL import Image as PILImage
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

def generate_thumbnail(image, height):
    
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
