from django.contrib.auth.models import AbstractUser
from django.db import models
from math import sin, cos, sqrt, atan2, radians

"""
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

"""

class Usuario(AbstractUser):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    money = models.IntegerField(default=0)
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    ida = models.CharField(max_length=50, default="None")
    manejo = models.BooleanField(default=False)


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
        return distance < 3
    
    def quiero_manejar(self, tramo, hora, dia, capacidad=4):
        try:
             self.auto.delete()
        except:
            pass
        auto = Auto(conductor=self, capacidad=capacidad, hora=hora, ida=tramo, dia=dia)
        auto.save()
        pasajeros = Pasajeros(auto=auto)
        pasajeros.save()
        self.save()
    
    def quiero_viaje(self, tramo, hora, dia):
        try:
             self.buscandoviaje.delete()
        except:
            pass
        print("Creee mi viajee")
        viaje = BuscandoViaje(user=self, hora=hora, ida=tramo, dia=dia)
        viaje.save()
        self.save()
    
    
class Auto(models.Model):
    conductor = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    capacidad = models.IntegerField(default=4)
    hora = models.CharField(max_length=6)
    ida = models.CharField(max_length=10)
    dia = models.DateField()

    def tengo_capacidad(self):
        pas = len(self.pasajeros.users.all())
        if pas >= self.capacidad:
            return False
        else:
            return (self.capacidad - pas)

class Pasajeros(models.Model):
    auto = models.OneToOneField(Auto, on_delete=models.CASCADE)
    users = models.ManyToManyField(Usuario)

    def agregar_pasajero(self, pasajero):
        pasajero.buscandoviaje.delete()
        self.users.add(pasajero)
        self.save()
        pasajero.save()
    
    def posibles_pasajeros(self):
        print("----------------------------------------------------------------------------------------------------------------")
        try:
            lista_final = []
            print("entre al try")
            print(BuscandoViaje.objects.all())
            for posible in BuscandoViaje.objects.all():
                print(posible.user)
                print(self.auto)
                print(Usuario.objects.get(id=posible.user))
                if self.auto.conductor.ubicacion_cercana(posible.user):
                    lista_final.append(posible.user)
            return lista_final
        except:
            return []

    def __str__(self):
        return self.auto.modelo

class BuscandoViaje(models.Model):
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    hora = models.CharField(max_length=6)
    ida = models.CharField(max_length=10)
    dia = models.DateField()
