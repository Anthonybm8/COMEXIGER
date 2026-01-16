from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import api_disponibilidad_list, api_disponibilidad_detail, api_disponibilidad_stats, api_disponibilidad_salida

router = DefaultRouter()
router.register(r'disponibilidad', views.DisponibilidadViewSet, basename='disponibilidad')

urlpatterns = [

    path('dispo', views.inicio, name='dispo'),
    path('eliminar_disponibilidad/<int:id>', views.eliminar_disponibilidad, name='eliminar_disponibilidad'),
    path('procesar_edicion_disponibilidad', views.procesar_edicion_disponibilidad, name='procesar_edicion_disponibilidad'),

    path('api/', include(router.urls)),
    path('api/disponibilidades/', views.api_disponibilidad_list, name='api-disponibilidad-list'),
    path('api/disponibilidades/<int:pk>/', views.api_disponibilidad_detail, name='api-disponibilidad-detail'),
    path('api/disponibilidades/stats/', views.api_disponibilidad_stats, name='api-disponibilidad-stats'),
    
    path('api/disponibilidades/salida/', api_disponibilidad_salida),
]
