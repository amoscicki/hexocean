from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Thumbnail_size(models.Model):
    height = models.IntegerField(null=False, blank=False, primary_key=True)
    def __str__(self):
        return str(self.height)

class Plan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    expiring_link = models.BooleanField(default=False)
    original_available = models.BooleanField(default=False)

    #assigned thumbnail sizes
    thumbnail_sizes = models.ManyToManyField(Thumbnail_size, blank=True)

    def __str__(self):
        return self.name
    

class CustomUser(AbstractUser):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username
