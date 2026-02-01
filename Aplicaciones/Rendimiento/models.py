# Rendimiento/models.py
from django.db import models
from django.utils import timezone
from datetime import datetime

from decimal import Decimal, ROUND_FLOOR

def hora_a_decimal_excel(dt):
 
    return float(f"{dt.hour}.{dt.minute:02d}")


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
    rendimiento = models.IntegerField(default=0)   # ej: 20
    ramos_base = models.IntegerField(default=0)    # (este NO lo usas en fórmula; tu base real sale del cálculo)

    bonches = models.IntegerField(default=0)       # reales

    # Campos calculados
    horas_trabajadas = models.FloatField(null=True, blank=True)
    ramos_esperados = models.FloatField(null=True, blank=True)   # = RAMOS BASE (Excel)
    ramos_extras = models.FloatField(null=True, blank=True)
    extras_por_hora = models.FloatField(null=True, blank=True)   # = HORAS GANADAS (Excel)

    from decimal import Decimal, ROUND_FLOOR

    def recalcular(self):
        if self.hora_inicio and self.hora_final and self.rendimiento is not None:

            # 1) Horas trabajadas usando tu regla Excel: (20.3 - 7) - 1
            inicio_fake = hora_a_decimal_excel(self.hora_inicio)
            final_fake  = hora_a_decimal_excel(self.hora_final)

            horas = (final_fake - inicio_fake) - 1
            if horas < 0:
                horas = 0

            # Horas trabajadas con 2 decimales
            self.horas_trabajadas = round(horas, 2)

            # 2) Ramos base = rendimiento * horas_trabajadas
            #    (aplicando tu regla de redondeo por la décima)
            horas_dec = Decimal(str(self.horas_trabajadas))
            rend_dec = Decimal(str(int(self.rendimiento)))

            base_raw = rend_dec * horas_dec
            base_floor = base_raw.to_integral_value(rounding=ROUND_FLOOR)
            frac = base_raw - base_floor

            decima = int((frac * Decimal("10")).to_integral_value(rounding=ROUND_FLOOR))

            if decima >= 5 and frac > 0:
                base_final = int(base_floor) + 1
            else:
                base_final = int(base_floor)

            # Este es tu "Ramos base" del Excel (aunque se llame ramos_esperados)
            self.ramos_esperados = float(base_final)

            # 3) Ramos extras = reales - ramos base
            self.ramos_extras = round(self.bonches - self.ramos_esperados, 2)

            # 4) Horas ganadas = ramos_extras / rendimiento
            self.extras_por_hora = round(self.ramos_extras / self.rendimiento, 2) if self.rendimiento > 0 else 0

        else:
            self.horas_trabajadas = None
            self.ramos_esperados = None
            self.ramos_extras = None
            self.extras_por_hora = None


    def save(self, *args, **kwargs):
        print(" [MODEL] save() llamado - ID:", self.id)
        self.recalcular()
        super().save(*args, **kwargs)



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