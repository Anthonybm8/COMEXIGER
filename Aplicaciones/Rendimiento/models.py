
from django.db import models
class QRUsado(models.Model):
    qr_id = models.CharField(max_length=255, unique=True)
    fecha_escaneo = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qr_id

class Rendimiento(models.Model):

    qr_id = models.CharField(max_length=255)
    numero_mesa = models.CharField(max_length=50)
    fecha_entrada = models.DateTimeField() 

    # Datos que llegan desde la app
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_final = models.DateTimeField(null=True, blank=True)

    # Datos base configurables
    rendimiento = models.IntegerField(default=0)   
    ramos_base = models.IntegerField(default=0)    

  
    bonches = models.IntegerField(default=0)       

    # Campos calculados (no se envían desde la app)
    horas_trabajadas = models.FloatField(null=True, blank=True)
    ramos_esperados = models.FloatField(null=True, blank=True)
    ramos_extras = models.FloatField(null=True, blank=True)
    extras_por_hora = models.FloatField(null=True, blank=True)

    def recalcular(self):
        if self.hora_inicio and self.hora_final:
            delta = self.hora_final - self.hora_inicio
            horas = (delta.total_seconds() / 3600) - 1  # descanso de 1 hora
            if horas < 0:
                horas = 0

            self.horas_trabajadas = round(horas, 2)
            self.ramos_esperados = round(self.rendimiento * horas, 2)
            self.ramos_extras = round(self.bonches - self.ramos_esperados, 2)

            if self.rendimiento > 0:
                self.extras_por_hora = round(self.ramos_extras / self.rendimiento, 2)
            else:
                self.extras_por_hora = 0
        else:
            # Aún no hay horas → no se calcula nada
            self.horas_trabajadas = None
            self.ramos_esperados = None
            self.ramos_extras = None
            self.extras_por_hora = None


