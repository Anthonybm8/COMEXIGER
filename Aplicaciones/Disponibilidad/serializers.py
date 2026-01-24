from rest_framework import serializers
from .models import Disponibilidad

from .models import Variedad

class VariedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variedad
        fields = ["id", "nombre", "fecha_creacion"]
class DisponibilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disponibilidad
        fields = '__all__'


class DisponibilidadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disponibilidad
        fields = [
            'numero_mesa',
            'variedad',
            'medida',
            'stock',
            'fecha_entrada',
            'fecha_salida'
        ]
