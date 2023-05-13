from django.contrib import admin
from .models import Bus, Reservation, Passenger, Blog
# Register your models here.
admin.site.register(Bus)
admin.site.register(Reservation)
admin.site.register(Passenger)
admin.site.register(Blog)