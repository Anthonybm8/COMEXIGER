from django.db import models
from django.utils import timezone

class Disponibilidad(models.Model):
    numero_mesa = models.PositiveIntegerField(verbose_name="Número de mesa")
    variedad = models.CharField(max_length=100)
    medida = models.CharField(max_length=50)

    stock = models.PositiveIntegerField(default=0)

    fecha_entrada = models.DateTimeField()
    fecha_salida = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Mesa {self.numero_mesa} - {self.variedad} ({self.stock})"
