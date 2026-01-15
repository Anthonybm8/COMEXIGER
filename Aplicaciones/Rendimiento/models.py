# Rendimiento/models.py
from django.db import models
from django.utils import timezone
from datetime import datetime

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

    def __str__(self):
        return f"Mesa {self.numero_mesa} - {self.fecha_entrada.date()}"

# 🔥 NUEVO MODELO: JornadaLaboral - Movido a Rendimiento
class JornadaLaboral(models.Model):
    ESTADOS = [
        ('iniciada', 'Jornada Iniciada'),
        ('finalizada', 'Jornada Finalizada'),
    ]
    
    # Usaremos el username directamente en lugar de ForeignKey
    usuario_username = models.CharField(max_length=150)
    usuario_nombre = models.CharField(max_length=100)
    mesa = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)
    hora_inicio = models.DateTimeField()
    hora_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='iniciada')
    horas_trabajadas = models.FloatField(null=True, blank=True)
    
    class Meta:
        # Un usuario solo puede tener una jornada por día
        unique_together = [['usuario_username', 'fecha']]
        ordering = ['-fecha', '-hora_inicio']
    
    def __str__(self):
        return f"{self.usuario_username} - {self.fecha} ({self.estado})"
    
    def calcular_horas_trabajadas(self):
        if self.hora_inicio and self.hora_fin:
            delta = self.hora_fin - self.hora_inicio
            # Restamos 1 hora de descanso si la jornada es mayor a 4 horas
            horas_brutas = delta.total_seconds() / 3600
            if horas_brutas > 4:
                self.horas_trabajadas = round(horas_brutas - 1, 2)
            else:
                self.horas_trabajadas = round(horas_brutas, 2)
        else:
            self.horas_trabajadas = 0
    
    def save(self, *args, **kwargs):
        if self.hora_fin:
            self.calcular_horas_trabajadas()
            self.estado = 'finalizada'
        super().save(*args, **kwargs)