from django.urls import path
from . import views  # Solo views, NO api_views

urlpatterns = [
    path('iniciose', views.inicio, name='iniciose'),
    path('cerrarsesion', views.cerrarsesion, name='cerrarsesion'),
    path('usuariore', views.inicios, name='usuariore'),
    path('nuevo_usuario', views.nuevo_usuario, name='nuevo_usuario'),
    path('guardar_usuario', views.guardar_usuario, name='guardar_usuario'),
    path('procesar_edicion_usuario', views.procesar_edicion_usuario, name='procesar_edicion_usuario'),
    path('eliminar_usuario/<int:id>', views.eliminar_usuario, name='eliminar_usuario'),
    
    # NO INCLUIR RUTAS API AQUÍ - van en COMEXIGER/urls.py
]