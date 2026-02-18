from django.urls import path
from . import views 

urlpatterns = [
    path('account-deletion', views.account_deletion, name='account_deletion'),
    path('iniciose', views.inicio, name='iniciose'),
    path('cerrarsesion', views.cerrarsesion, name='cerrarsesion'),
    path('usuariore', views.inicios, name='usuariore'),
    path('nuevo_usuario', views.nuevo_usuario, name='nuevo_usuario'),
    path("guardar_mesa", views.guardar_mesa, name="guardar_mesa"),
    path('guardar_usuario', views.guardar_usuario, name='guardar_usuario'),
    path('procesar_edicion_usuario', views.procesar_edicion_usuario, name='procesar_edicion_usuario'),
    path('eliminar_usuario/<int:id>', views.eliminar_usuario, name='eliminar_usuario'),
    
    
    
    

]
