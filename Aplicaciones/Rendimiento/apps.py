from django.apps import AppConfig


class RendimientoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Aplicaciones.Rendimiento'
    def ready(self):
        import Aplicaciones.Rendimiento.signals
