from rest_framework import serializers
from .models import Rendimiento

class RendimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rendimiento
        fields = '__all__'

class RendimientoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rendimiento
        fields = ['numero_mesa', 'variedad', 'medida', 'bonches', 'fecha_entrada', 'fecha_salida']