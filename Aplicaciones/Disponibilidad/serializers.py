from rest_framework import serializers
from .models import Disponibilidad


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
