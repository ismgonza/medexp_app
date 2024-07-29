# locations/models.py
from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    canton = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
