from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse



class Bus(models.Model):
    bus_name = models.CharField(max_length=30)
    source = models.CharField(max_length=30)
    dest = models.CharField(max_length=30)
    nbr_passager = models.DecimalField(decimal_places=0, max_digits=2)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return self.bus_name
class Passenger(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    numero = models.CharField(max_length=11)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Reservation(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    statut_paiement = models.CharField(max_length=10, default='UNPAID')    
    nombre_de_places = models.PositiveIntegerField(default=1)


    def get_absolute_url(self):
        url = reverse('reserve_confirm', args=[str(self.bus.id), str(self.date_reservation)])
        return url

    
    def __str__(self):
        return f"{self.passenger.nom} {self.passenger.prenom} ({self.bus}) le {self.reservation_date}"


class Blog(models.Model):
    titre = models.CharField(max_length=100)
    overview = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.titre
    
    