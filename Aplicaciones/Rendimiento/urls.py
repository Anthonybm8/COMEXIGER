from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'rendimiento', views.RendimientoViewSet, basename='rendimiento')

urlpatterns = [
    path('rendimiento', views.inicio, name='rendimiento'),
    path('nuevo_rendimiento', views.nuevo_rendimiento, name='nuevo_rendimiento'),
    path('guardar_rendimiento', views.guardar_rendimiento, name='guardar_rendimiento'),
    path('eliminar_rendimiento/<int:id>', views.eliminar_rendimiento, name='eliminar_rendimiento'),
    path('procesar_edicion_rendimiento', views.procesar_edicion_rendimiento, name='procesar_edicion_rendimiento'),


    path('api/', include(router.urls)),
    path('api/rendimientos/', views.api_rendimiento_list, name='api-rendimiento-list'),
    path('api/rendimientos/<int:pk>/', views.api_rendimiento_detail, name='api-rendimiento-detail'),
    path('api/rendimientos/stats/', views.api_rendimiento_stats, name='api-rendimiento-stats'),

]
