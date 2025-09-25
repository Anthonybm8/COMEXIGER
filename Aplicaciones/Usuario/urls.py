from django.urls import path
from . import views

urlpatterns = [
    path('iniciose', views.inicio, name='iniciose'),
    path('cerrarsesion', views.cerrarsesion,name='cerrarsesion'),
]