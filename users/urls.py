# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('<int:pk>/ubicaciones/', views.UbicacionIndex.as_view(), name='ubicacion'),
    path('<int:pk>/newubicacion/', views.newubicacion, name='newubicacion'),
    path('<int:pk>/editubicacion/', views.newubicacion, name='editubicacion'),
]