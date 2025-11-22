from django.db.models import Sum 
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import Rendimiento
# de la apli 
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .serializers import RendimientoSerializer, RendimientoCreateSerializer

def inicio(request):
    listadoRendimiento=Rendimiento.objects.all()
    return render(request, 'rendimiento.html',{'rendimiento':listadoRendimiento})

def nuevo_rendimiento(request):
    return render(request, "nuevo_rendimiento.html")

def guardar_rendimiento(request):
    if request.method == "POST":
        numero_mesa = request.POST["numero_mesa"]
        variedad = request.POST["variedad"]
        medida = request.POST["medida"]
        bonches = request.POST["bonches"]
        fecha_entrada = request.POST["fecha_entrada"]
        fecha_salida = request.POST["fecha_salida"]

        nuevo = Rendimiento.objects.create(
            numero_mesa=numero_mesa,
            variedad=variedad,
            medida=medida,
            bonches=bonches,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida if fecha_salida else None
        )

        messages.success(request, "Rendimiento guardado exitosamente")
        return redirect('rendimiento')
    else:
        messages.error(request, "Error al guardar rendimiento")
        return redirect('nuevo_rendimiento')

def eliminar_rendimiento(request, id):
    rendimiento_eliminar = Rendimiento.objects.get(id=id)
    rendimiento_eliminar.delete()
    messages.success(request, "Rendimiento eliminado exitosamente")
    return redirect('rendimiento')

def procesar_edicion_rendimiento(request):
    if request.method == "POST":
        try:
            id = request.POST["id"]
            rendimiento = Rendimiento.objects.get(id=id)

            rendimiento.numero_mesa = request.POST["numero_mesa"]
            rendimiento.variedad = request.POST["variedad"]
            rendimiento.medida = request.POST["medida"]
            rendimiento.bonches = request.POST["bonches"]

            fecha_entrada = request.POST.get("fecha_entrada")
            fecha_salida = request.POST.get("fecha_salida")

            if fecha_entrada:
                rendimiento.fecha_entrada = datetime.strptime(fecha_entrada, "%Y-%m-%dT%H:%M")
            if fecha_salida:
                rendimiento.fecha_salida = datetime.strptime(fecha_salida, "%Y-%m-%dT%H:%M")
            else:
                rendimiento.fecha_salida = None

            rendimiento.save()
            messages.success(request, "Rendimiento actualizado correctamente ")
        except Exception as e:
            messages.error(request, f"Error al procesar la edición: {e}")
        return redirect('rendimiento')


# ========== VISTAS API PARA FLUTTER ==========

class RendimientoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver y editar rendimientos
    """
    queryset = Rendimiento.objects.all().order_by('-fecha_entrada')
    serializer_class = RendimientoSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Endpoint personalizado: /api/rendimiento/activos/
        Retorna solo rendimientos sin fecha de salida
        """
        rendimientos_activos = Rendimiento.objects.filter(fecha_salida__isnull=True)
        serializer = self.get_serializer(rendimientos_activos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_mesa(self, request):
        """
        Endpoint personalizado: /api/rendimiento/por_mesa/?mesa=1
        Filtra rendimientos por número de mesa
        """
        numero_mesa = request.query_params.get('mesa', None)
        if numero_mesa:
            rendimientos = Rendimiento.objects.filter(numero_mesa=numero_mesa)
            serializer = self.get_serializer(rendimientos, many=True)
            return Response(serializer.data)
        return Response({"error": "Parámetro 'mesa' requerido"}, status=400)

# Vistas basadas en funciones para API
@api_view(['GET', 'POST'])
def api_rendimiento_list(request):
    """
    Lista todos los rendimientos o crea uno nuevo
    """
    if request.method == 'GET':
        rendimientos = Rendimiento.objects.all().order_by('-fecha_entrada')
        serializer = RendimientoSerializer(rendimientos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RendimientoCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def api_rendimiento_detail(request, pk):
    """
    Obtener, actualizar o eliminar un rendimiento específico
    """
    try:
        rendimiento = Rendimiento.objects.get(pk=pk)
    except Rendimiento.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RendimientoSerializer(rendimiento)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RendimientoSerializer(rendimiento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        rendimiento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_rendimiento_stats(request):
    """
    Estadísticas para dashboard de Flutter
    """
    total_rendimientos = Rendimiento.objects.count()
    rendimientos_activos = Rendimiento.objects.filter(fecha_salida__isnull=True).count()
    total_bonches = Rendimiento.objects.aggregate(Sum('bonches'))['bonches__sum'] or 0

    stats = {
        'total_rendimientos': total_rendimientos,
        'rendimientos_activos': rendimientos_activos,
        'total_bonches': total_bonches,
        'mesas_activas': Rendimiento.objects.filter(fecha_salida__isnull=True)
                            .values('numero_mesa')
                            .distinct()
                            .count()
    }
    return Response(stats)