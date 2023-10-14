from django.db import models
from accounts.models import CustomUser, Thumbnail_size
from django.utils import timezone

# Create your models here.
def get_upload_path(instance, filename):
    return f'{instance.user.id}/{timezone.now().date()}/{filename}'

class Image(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_path, null=False, blank=False)
    height = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return self.image.name


class Link(models.Model):
    image = models.ForeignKey(Image, on_delete=models.PROTECT)
    link = models.URLField(null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)
    expires_at = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return self.link
