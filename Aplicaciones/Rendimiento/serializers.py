from rest_framework import serializers
from .models import Rendimiento

class RendimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rendimiento
        fields = '__all__'

