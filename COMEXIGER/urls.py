from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from Aplicaciones.Disponibilidad.views import listar_variedades_api

from Aplicaciones.Usuario.refresh_api import refresh_token_api

# Importar APIs de Usuario
from Aplicaciones.Usuario.api_views import (
    registrar_usuario_api, 
    login_usuario_api,
    obtener_mesas_api,
    verificar_mesa_api
)

# Importar APIs de Rendimiento (Jornada)
from Aplicaciones.Rendimiento.api_views import (
    iniciar_jornada_api,
    finalizar_jornada_api,
    obtener_jornada_actual_api,
    obtener_historial_jornadas_api
)

urlpatterns = [
    # Redirección
    path('', RedirectView.as_view(url=reverse_lazy('iniciose'), permanent=False)),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps normales (web)
    path('', include('Aplicaciones.Disponibilidad.urls')),
    path('', include('Aplicaciones.Usuario.urls')),
    path('', include('Aplicaciones.Rendimiento.urls')),
    
    # 🔥 RUTAS API PARA FLUTTER - USUARIO
    path('api/registrar/', registrar_usuario_api, name='api_registrar'),
    path('api/login/', login_usuario_api, name='api_login'),
    path('api/mesas/', obtener_mesas_api, name='api_mesas'),
    path('api/verificar_mesa/', verificar_mesa_api, name='api_verificar_mesa'),
    
    # 🔥 RUTAS API PARA FLUTTER - JORNADA LABORAL
    path('api/jornada/iniciar/', iniciar_jornada_api, name='api_jornada_iniciar'),
    path('api/jornada/finalizar/', finalizar_jornada_api, name='api_jornada_finalizar'),
    path('api/jornada/actual/', obtener_jornada_actual_api, name='api_jornada_actual'),
    path('api/jornada/historial/', obtener_historial_jornadas_api, name='api_jornada_historial'),
    
    path('api/variedades/', listar_variedades_api, name='api_variedades'),

    path("api/token/refresh/", refresh_token_api, name="api_token_refresh"),


]

# Debug
print("="*60)
print("✅ SERVIDOR DJANGO INICIADO")
print("✅ APIs DISPONIBLES:")
print("   • POST http://localhost:8000/api/registrar/")
print("   • POST http://localhost:8000/api/login/")
print("   • GET  http://localhost:8000/api/mesas/")
print("   • POST http://localhost:8000/api/verificar_mesa/")
print("   • POST http://localhost:8000/api/jornada/iniciar/")
print("   • POST http://localhost:8000/api/jornada/finalizar/")
print("   • GET  http://localhost:8000/api/jornada/actual/")
print("   • GET  http://localhost:8000/api/jornada/historial/")
print("="*60)