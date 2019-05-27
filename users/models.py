from django.contrib.auth.models import AbstractUser
from django.db import models
from math import sin, cos, sqrt, atan2, radians

class CustomUser(AbstractUser):
    # add additional fields in here
    conductor = models.BooleanField(default=False)
    tengo_ida = models.BooleanField(default=False)
    id_conductor = models.CharField(default='None', max_length=20)
    
    def __str__(self):
        return self.email
    
    def conductores_posibles(self):
        users = CustomUser.objects.all()
        users = [user for user in users if user.tengo_ubicacion()]
        posibles = [user for user in users if self.ubicacion.ubicacion_cercana(user.ubicacion) and user != self and user.conductor]
        posibles = [user for user in posibles if user.auto.tengo_capacidad()]
        return(posibles)
    
    def tengo_ubicacion(self):
        try:
            self.ubicacion
            return True
        except:
            return False
    
    def me_lleva(self):
        me_lleva = CustomUser.objects.get(id=self.id_conductor)
        return me_lleva


class UbicacionManager(models.Manager):
    def create_ubicacion(self, user, direccion,lat, lng):
        ubicacion = Ubicacion(user=user, lat=lat, lng=lng)
        return ubicacion

class Ubicacion(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200, default='Campus San Joaquín, Pontificia Universidad Católica de Chile')
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    objects = UbicacionManager()

    def ubicacion_cercana(self, ubicacion):
        R = 6373
        lat1 = radians(self.lat)
        lng1 = radians(self.lng)
        lat2 = radians(ubicacion.lat)
        lng2 = radians(ubicacion.lng)

        dlon = lng2 - lng1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance < 5


class Auto(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    capacidad = models.IntegerField(default=4)
    color = models.CharField(default='negro', max_length=50)
    modelo = models.CharField(default='Mazda 2', max_length=50)

    def tengo_capacidad(self):
        pas = len(self.pasajeros.user.all())
        if pas >= self.capacidad:
            return False
        else:
            return (self.capacidad - pas)

class Pasajeros(models.Model):
    auto = models.OneToOneField(Auto, on_delete=models.CASCADE)
    user = models.ManyToManyField(CustomUser)

    def __str__(self):
        return self.auto.modelo