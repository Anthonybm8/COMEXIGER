from django.urls import path
from . import views
from .consumers import DisponibilidadConsumer

urlpatterns = [
    path('disponibilidad/', views.inicio, name='dispo'),
]
