from django.db import models
from accounts.models import CustomUser

# Create your models here.
def get_upload_path(instance, filename):
    return f'{instance.user.id}/{filename}'

class Image(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_path, null=False, blank=False)
    height = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return self.image.name


class Link(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=False, blank=False)
    expires_at = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return f'{self.image.image.name} - {self.created_at} - {self.expires_at}'
