from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="index"),

    path('login', views.log, name="login"),
    path('logout', views.logoutUser, name="logout"),
    path('register', views.register_view, name="register"),
    path('bus_detail/<int:id>', views.bus_detail, name="bus_detail"),
    path('toutes-les-bus', views.bus_all, name="bus"),
    path('findbus', views.findbus, name="finbus"),
    path('remerciement',views.remerciement,name="remerciement" ),
    path('reserve/<int:id>/', views.reserve, name='reserve'),    
    path('reserve_confirm/<int:id>/', views.reserve_confirm, name='reserve_confirm'),    path('apropos', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('about',views.about, name="about")

]
