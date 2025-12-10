from django.apps import AppConfig


class DisponibilidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Aplicaciones.Disponibilidad'
    
    def ready(self):
        import Aplicaciones.Disponibilidad.signals
    
