from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
import requests

from .forms import CustomUserCreationForm, UbicacionForm, NewAutoForm
from .models import Ubicacion, CustomUser, Pasajeros

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UbicacionIndex(generic.ListView):
    template_name = 'users/ubicacionindex.html'
    context_object_name = 'ubicaciones'

    def get_queryset(self):
        return Ubicacion.objects.filter(user_id=self.kwargs['pk'])

def newubicacion(request, pk):
    if request.method == "POST":
        form = UbicacionForm(request.POST)
        if form.is_valid():
            try: 
                request.user.ubicacion.delete()
            finally:   
                post = form.save(commit=False)
                direccion = post.direccion
                post.user = request.user
                GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
                API_KEY = 'AIzaSyA-CcE8x7D-gKr8Hoo2rQ2vyGP4pe8ryQQ'
                params = {
                    'address': direccion,
                    'region': 'chile',
                    'key': API_KEY
                }
                req = requests.get(GOOGLE_MAPS_API_URL, params=params)
                res = req.json()['results'][0]
                post.lat = res['geometry']['location']['lat']
                post.lng = res['geometry']['location']['lng']
                success_url = reverse_lazy('home')
                post.save()
                return HttpResponseRedirect(success_url)
    else:
        form = UbicacionForm()
    return render(request, 'users/newubicacion.html', {'form': form})

def newauto(request, pk):
    if request.method == "POST":
        form = NewAutoForm(request.POST)
        if form.is_valid():
            try:
                request.user.auto.delete()
            finally:   
                post = form.save(commit=False) 
                post.user = request.user
                success_url = reverse_lazy('home')
                post.save()
                request.user.auto.pasajeros = Pasajeros(auto=request.user.auto)
                request.user.auto.pasajeros.save()
                request.user.auto.save()
                return HttpResponseRedirect(success_url)
    else: 
        form = NewAutoForm()
    return render(request, 'users/newauto.html', {'form': form})

def conductor(request, pk):
    if request.user.conductor:
        request.user.conductor = False
        request.user.tengo_ida = False
        usuarios = request.user.auto.pasajeros.user.all()
        for user in usuarios:
            request.user.auto.pasajeros.user.remove(user)
            user.tengo_ida = False
            user.conductor = False
            user.id_conductor = 'None'
            user.save()

    else:
        request.user.conductor = True
        request.user.tengo_ida = True
    request.user.save()
    return HttpResponseRedirect(reverse_lazy('home'))

def newllevame(request, pk):
    solicitante = request.user
    if solicitante.tengo_ida:
        maneja = CustomUser.objects.get(id=pk)
        maneja.auto.pasajeros.user.remove(solicitante)
        solicitante.tengo_ida = False
        solicitante.id_conductor = "None"
        solicitante.save()
    else:
        maneja = CustomUser.objects.get(id=pk)
        maneja.auto.pasajeros.user.add(solicitante)
        solicitante.tengo_ida = True
        solicitante.id_conductor = maneja.id
        solicitante.save()
    return HttpResponseRedirect(reverse_lazy('home'))

def nollevar(request, pk):
    maneja = request.user
    solicitante = CustomUser.objects.get(id=pk)
    maneja.auto.pasajeros.user.remove(solicitante)
    solicitante.tengo_ida = False
    solicitante.id_conductor = "None"
    solicitante.save()
    solicitante.save()
    return HttpResponseRedirect(reverse_lazy('home'))


    

