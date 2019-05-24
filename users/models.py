from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # add additional fields in here

    def __str__(self):
        return self.email


class UbicacionManager(models.Manager):
    def create_ubicacion(self, user, lat, lng):
        ubicacion = Ubicacion(user=user, lat=lat, lng=lng)
        return ubicacion

class Ubicacion(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    lat = models.IntegerField(default=0)
    lng = models.IntegerField(default=0)
    objects = UbicacionManager()