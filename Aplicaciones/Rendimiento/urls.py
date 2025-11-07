from django.urls import path
from . import views

urlpatterns = [
    path('rendimiento', views.inicio, name='rendimiento'),
    path('nuevo_rendimiento', views.nuevo_rendimiento, name='nuevo_rendimiento'),
    path('guardar_rendimiento', views.guardar_rendimiento, name='guardar_rendimiento'),
    path('eliminar_rendimiento/<int:id>', views.eliminar_rendimiento, name='eliminar_rendimiento'),
    path('procesar_edicion_rendimiento', views.procesar_edicion_rendimiento, name='procesar_edicion_rendimiento'),

]
