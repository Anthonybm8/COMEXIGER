from django.urls import path
from . import views

urlpatterns = [
    path('disponibilidad/', views.inicio, name='dispo'),
]
