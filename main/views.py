import datetime
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import *
import datetime as dt
from reportlab.lib.pagesizes import landscape, A4
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import qrcode
import os
import io
from PIL import Image
from reportlab.lib.utils import ImageReader
from django.db.models.signals import post_save
#from twilio.rest import Client
from django.dispatch import receiver
from reportlab.lib.pagesizes import letter
from django.contrib.auth.decorators import login_required


def home(request):
    bus = Bus.objects.filter(date__gte=dt.datetime.now().date())
    current_time = dt.datetime.now().strftime('%H:%M:%S')
    sources = Bus.objects.order_by().values_list('source', flat=True).distinct()
    dests = Bus.objects.order_by().values_list('dest', flat=True).distinct()
    blog = Blog.objects.all().order_by('-id')[:3]

    context ={
            'bus':bus,
            'current_time': current_time,
            'sources':sources,
            'dests' :dests,
            'blog':blog,

        }
    if request.user.is_authenticated:
        
        if request.method == 'POST':
                source = request.POST.get('source')
                dest = request.POST.get('dest')
                date = request.POST.get('date')
                bus_list = Bus.objects.filter(source =source, dest=dest, date=date)
                bus_count = bus_list.count()
                if source == dest:
                    context["error"] = "Vous ne pouvez pas chercher un bus entre deux meme villes !"
                    return render(request, 'main/index.html',context )
                
                if bus_list:
                    return render(request, 'main/trouver_bus.html',{'bus_list':bus_list, 'bus_count':bus_count})
                else:
                    context["error"] = "Il n'y a pas de bus disponible aujourd'hui entre ces villes"
                    return render(request, 'main/trouver_bus.html', context)
        else:
                return render(request, 'main/index.html', context)

        
    else:
        return render(request, 'main/index.html', context)


def bus_all(request):
    bus = Bus.objects.filter(date__gte=dt.datetime.now().date())
    return render(request,'main/bus_all.html',{'bus':bus})

@login_required
def bus_detail(request,id):
    bus = Bus.objects.get(id=id)
    return render(request, "main/bus_detail.html", {'bus':bus})

def log(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error( "Utilisateur n'existe pas")
        user = authenticate(request, username =username, password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.error(request, 'Username or password is not correct')
                
    
    return render(request, 'main/login.html')

def logoutUser(request):
    logout(request)
    return redirect( 'index')

def footerblog(request):
    footbus = Bus.objects.all()

    content = {
        'footbus':footbus
    }
    return render(request, 'main/layout.html')
def register_view(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        username = request.POST["username"]
        email = request.POST["email"]


        # Ensuring password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "main/register.html", {
                "message": "ces mot de passe ne sont identiques."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.save()
        except:
            return render(request, "main/register.html", {
                "message": "Ces champs sont obligatoires."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "main/register.html")



def contact(request):
    return render(request, 'main/contact.html')
def about(request):
    return render(request,'main/about.html')


def findbus(request):
    context = {}
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date=date_r)
        if bus_list:
            return render(request, 'main/trouver_bus.html', locals())
        else:
            context["error"] = "Aucun bus disponible pour le moment"
            return render(request, 'main/trouver_bus.html', context)
    else:
        return render(request, 'main/index.html')

@login_required()
def reserve_confirm(request, id):
    bus = Bus.objects.get(id=id)
    context = {'bus': bus, }
    return render(request, 'main/reserve_confirm.html', context)


def reserve(request, id):
    if request.method == 'POST':
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        numero = request.POST['numero']
        email = request.POST['email']
        nombre_de_place = request.POST['nombre_de_place']
        bus = Bus.objects.get(id=id)
        reservation_date = dt.datetime.now().date()
        passenger = Passenger.objects.create(nom=nom, prenom=prenom,numero=numero, email=email)
        reservation = Reservation.objects.create(bus=bus, passenger=passenger, nombre_de_places=nombre_de_place, reservation_date=reservation_date)
        statut_paiement = Reservation.statut_paiement
        bus.save()

        if statut_paiement == "PAID":
            bus.nbr_passager -= Decimal(nombre_de_place)       
        bus.save()
        
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(f'Reservation ID: {reservation.id}, Nombre de place: {nombre_de_place}')
        qr.make(fit=True)
        img = qr.make_image(fill_color='white', back_color='#000')
        


        # Render image and add to PDF
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()

        # create a HTTP response with the PDF data and content type
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{passenger.nom}_reservation_{reservation.id}.pdf"'

        # render the PDF
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(response, pagesize=(11.5*inch, 8*inch))
        pdf.setTitle(f"Facture de réservation - ID {reservation.id}")

        pdf.setFont("Helvetica-Bold", 11)        
        pdf.setFillColorRGB(0, 0, 0.5) # Dark blue

        # Set alignment options
        align_left = 3*inch
        align_top = 6*inch
        line_height = 0.5*inch

        # Add content to PDF
        pdf.drawString(align_left, align_top, "Facture de réservation")
        pdf.drawString(align_left, align_top - line_height, f"ID de réservation: {reservation.id}")
        pdf.drawString(align_left, align_top - 2*line_height, f"Nomdu passager: {nom}")
        pdf.drawString(align_left, align_top - 3*line_height, f"Prénom : {prenom}")
        pdf.drawString(align_left, align_top - 4*line_height, f"Destination: {bus.dest}")
        pdf.drawString(align_left, align_top - 5*line_height, f"Source: {bus.source}")
        pdf.drawString(align_left, align_top - 6*line_height, f"Nom de bus: {bus.bus_name}")
        pdf.drawString(align_left, align_top - 7*line_height, f"Nombre de place : {nombre_de_place}")
        pdf.drawString(align_left, align_top - 8*line_height, f"Total à payer : {nombre_de_place} x {bus.price} = {Decimal(nombre_de_place) * bus.price}")        


        # Add status of payment with a condition
        if statut_paiement == "PAID":
            pdf.setFillColorRGB(0, 0.5, 0) # Green
            pdf.drawString(align_left, align_top - 9*line_height, "Status de paiement: Payé")
        else:
            pdf.setFillColorRGB(0.5, 0, 0) # Red
            pdf.drawString(align_left, align_top - 9*line_height, "Status de paiement: En attente")

                # Add QR code to PDF
        img_width = 2*inch
        img_margin = 0.5*inch
        img_height = 2*inch
        img_x = 11*inch - img_margin - img_width
        img_y = 8*inch - img_margin - img_height

        # Add QR code to PDF
        pdf.drawImage(ImageReader(BytesIO(img_data)), img_x, img_y, width=img_width, height=img_height)

        # Save PDF
        pdf.showPage()
        pdf.save()
        
        # attach PDF to email
        
        messages.success(request, 'Le ticket a été téléchargé avec succès veuillez finaliser votre operation (voir +229 90776888)!')
        
        return response
    else:
        return redirect('index')


def remerciement(request):
    return render(request, 'main/remerciement.html')
@receiver(post_save, sender=Reservation)
def payment_status_update(sender, instance, **kwargs):
    if instance.statut_paiement == 'PAID':
        # Vous pouvez remplacer les valeurs ci-dessous par vos propres informations Twilio
        account_sid = 'AC6308d8830959f45d53fda9a8ccb09c1f'
        auth_token = '996547fa29114a1cfa140280695c2ca2'
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
                body=f"Votre réservation pour le bus {instance.bus.bus_name} a été payée.",
                from_='+22990776888',  # Remplacez par votre numéro Twilio
                to=f"+{instance.numero}"  # Remplacez par le numéro de téléphone du passager
            )

        print(message.sid)

