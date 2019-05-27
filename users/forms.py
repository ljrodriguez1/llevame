from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Ubicacion, Auto

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['direccion'] 

class NewAutoForm(forms.ModelForm):

    class Meta(UserCreationForm):
        model = Auto
        fields = ('modelo', 'color', 'capacidad')