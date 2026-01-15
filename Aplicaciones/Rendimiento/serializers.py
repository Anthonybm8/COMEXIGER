# Rendimiento/serializers.py
from rest_framework import serializers
from .models import Rendimiento, JornadaLaboral

class RendimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rendimiento
        fields = '__all__'
        read_only_fields = ['horas_trabajadas', 'ramos_esperados', 'ramos_extras', 'extras_por_hora']

class JornadaLaboralSerializer(serializers.ModelSerializer):
    class Meta:
        model = JornadaLaboral
        fields = [
            'id', 'usuario_username', 'usuario_nombre', 'mesa', 
            'fecha', 'hora_inicio', 'hora_fin', 'estado', 'horas_trabajadas'
        ]
        read_only_fields = ['fecha', 'horas_trabajadas']