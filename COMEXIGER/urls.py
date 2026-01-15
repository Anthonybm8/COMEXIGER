from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.urls import reverse_lazy

# Importar APIs directamente
from Aplicaciones.Usuario.api_views import (
    registrar_usuario_api, 
    login_usuario_api,
    obtener_mesas_api,
    verificar_mesa_api
)

urlpatterns = [
    # Redirección
    path('', RedirectView.as_view(url=reverse_lazy('iniciose'), permanent=False)),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps normales (web) - INCLUYE Usuario.urls también
    path('', include('Aplicaciones.Disponibilidad.urls')),
    path('', include('Aplicaciones.Usuario.urls')),  # ¡AHORA SÍ!
    path('', include('Aplicaciones.Rendimiento.urls')),
    
    # 🔥 RUTAS API PARA FLUTTER - SIN 'Usuario/' en el path
    path('api/registrar/', registrar_usuario_api, name='api_registrar'),
    path('api/login/', login_usuario_api, name='api_login'),
    path('api/mesas/', obtener_mesas_api, name='api_mesas'),
    path('api/verificar_mesa/', verificar_mesa_api, name='api_verificar_mesa'),
]

# Debug
print("="*60)
print("✅ SERVIDOR DJANGO INICIADO")
print("✅ APIs DISPONIBLES:")
print("   • POST http://localhost:8000/api/registrar/")
print("   • POST http://localhost:8000/api/login/")
print("   • GET  http://localhost:8000/api/mesas/")
print("   • POST http://localhost:8000/api/verificar_mesa/")
print("="*60)