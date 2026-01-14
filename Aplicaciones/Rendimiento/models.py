from django.db import models
from django.utils import timezone

class QRUsado(models.Model):
    qr_id = models.CharField(max_length=255, unique=True)
    fecha_escaneo = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qr_id
class Rendimiento(models.Model):
    qr_id = models.CharField(max_length=255)
    numero_mesa = models.CharField(max_length=50)
    variedad = models.CharField(max_length=100)
    medida = models.CharField(max_length=50)
    bonches = models.IntegerField(default=1)
    fecha_entrada = models.DateTimeField()
    fecha_salida = models.DateTimeField(null=True, blank=True)



