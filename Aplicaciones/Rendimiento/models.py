from django.db import models
from django.utils import timezone

class Rendimiento(models.Model):
    numero_mesa = models.PositiveIntegerField(verbose_name="Número de mesa")
    variedad = models.CharField(max_length=100)
    medida = models.CharField(max_length=50)
    bonches = models.PositiveIntegerField()
    fecha_entrada = models.DateTimeField(default=timezone.now)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    codigo_id = models.CharField(max_length=50,unique=True, null=True, blank=True)


