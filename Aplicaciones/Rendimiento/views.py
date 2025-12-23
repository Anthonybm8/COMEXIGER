from django.db.models import Sum 
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import Rendimiento

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .serializers import RendimientoSerializer
from django.utils import timezone

def inicio(request):
    listadoRendimiento = Rendimiento.objects.all()
    return render(request, 'rendimiento.html', {'rendimiento': listadoRendimiento})

def nuevo_rendimiento(request):
    return render(request, "nuevo_rendimiento.html")

def guardar_rendimiento(request):
    if request.method == "POST":
        numero_mesa = request.POST["numero_mesa"]
        variedad = request.POST["variedad"]
        medida = request.POST["medida"]
        bonches = int(request.POST["bonches"])
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

        # --- WebSocket notification ---
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "rendimientos",  # Nombre del grupo
            {
                "type": "nuevo_rendimiento",  # Llama al método en el consumer
                "data": RendimientoSerializer(nuevo).data
            }
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
            rendimiento.bonches = int(request.POST["bonches"])

            fecha_entrada = request.POST.get("fecha_entrada")
            fecha_salida = request.POST.get("fecha_salida")

            if fecha_entrada:
                rendimiento.fecha_entrada = datetime.strptime(fecha_entrada, "%Y-%m-%dT%H:%M")
            if fecha_salida:
                rendimiento.fecha_salida = datetime.strptime(fecha_salida, "%Y-%m-%dT%H:%M")
            else:
                rendimiento.fecha_salida = None

            rendimiento.save()

            # --- WebSocket notification ---
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {
                    "type": "nuevo_rendimiento",
                    "data": RendimientoSerializer(rendimiento).data
                }
            )

            messages.success(request, "Rendimiento actualizado correctamente ")
        except Exception as e:
            messages.error(request, f"Error al procesar la edición: {e}")
        return redirect('rendimiento')

# ------------------ API REST ------------------

class RendimientoViewSet(viewsets.ModelViewSet):
    queryset = Rendimiento.objects.all().order_by('-fecha_entrada')
    serializer_class = RendimientoSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        rendimientos_activos = Rendimiento.objects.filter(fecha_salida__isnull=True)
        serializer = self.get_serializer(rendimientos_activos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_mesa(self, request):
        numero_mesa = request.query_params.get('mesa', None)
        if numero_mesa:
            rendimientos = Rendimiento.objects.filter(numero_mesa=numero_mesa)
            serializer = self.get_serializer(rendimientos, many=True)
            return Response(serializer.data)
        return Response({"error": "Parámetro 'mesa' requerido"}, status=400)

@api_view(['GET', 'POST'])
def api_rendimiento_list(request):
    if request.method == 'GET':

    # ----- PARÁMETROS -----
        ordenar = request.query_params.get("ordenar")      # mesa | variedad | medida | fecha
        fecha_exacta = request.query_params.get("fecha")   # YYYY-MM-DD
        fecha_desde = request.query_params.get("desde")    # YYYY-MM-DD
        fecha_hasta = request.query_params.get("hasta")    # YYYY-MM-DD
        reciente = request.query_params.get("reciente")    # true / false

        rendimientos = Rendimiento.objects.all()

        # ----- FILTRO POR FECHA EXACTA -----
        if fecha_exacta:
            rendimientos = rendimientos.filter(fecha_entrada__date=fecha_exacta)

        # ----- FILTRO POR RANGO DE FECHAS -----
        if fecha_desde and fecha_hasta:
            rendimientos = rendimientos.filter(
                fecha_entrada__date__range=[fecha_desde, fecha_hasta]
            )

        # ----- ORDENAMIENTO FINAL (CORRECTO) -----
        order_fields = []

        # Campo a ordenar
        if ordenar == "mesa":
            order_fields.append("numero_mesa")
        elif ordenar == "variedad":
            order_fields.append("variedad")
        elif ordenar == "medida":
            order_fields.append("medida")
        elif ordenar == "fecha":
            order_fields.append("fecha_entrada")

        # Dirección (reciente / antiguo)
        if reciente == "true" and order_fields:
            order_fields[0] = "-" + order_fields[0]
        elif reciente == "true" and not order_fields:
            order_fields.append("-fecha_entrada")
        elif reciente == "false" and not order_fields:
            order_fields.append("fecha_entrada")

        # Aplicar UNA SOLA VEZ
        if order_fields:
            rendimientos = rendimientos.order_by(*order_fields)


        # ----- RESPUESTA -----
        serializer = RendimientoSerializer(rendimientos, many=True)
        return Response(serializer.data)


    elif request.method == 'POST':
        data = request.data

        codigo = data.get("codigo_id")
        mesa = data.get("numero_mesa")
        variedad = data.get("variedad")
        medida = data.get("medida")
        if not codigo or not mesa or not variedad or not medida:
            return Response({"error": "Datos incompletos"}, status=400)
        hoy = timezone.localdate()
        existente = Rendimiento.objects.filter(
            numero_mesa=mesa,
            variedad=variedad,
            medida=medida,
            fecha_entrada__date=hoy
        ).first()
        if existente:
            if existente.codigo_id == codigo:
                return Response({"msg": "QR repetido, escaneo ignorado"}, status=200)
            existente.bonches += 1
            existente.codigo_id = codigo
            existente.save()
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {
                    "type": "nuevo_rendimiento",
                    "data": RendimientoSerializer(existente).data
                }
            )

            return Response(RendimientoSerializer(existente).data, status=200)
            
        # Crear nuevo registro
        nuevo = Rendimiento.objects.create(
            codigo_id=codigo,
            numero_mesa=mesa,
            variedad=variedad,
            medida=medida,
            bonches=1,
            fecha_entrada=timezone.now(),
            fecha_salida=None
        )

        # WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "rendimientos",
            {
                "type": "nuevo_rendimiento",
                "data": RendimientoSerializer(nuevo).data
            }
        )

        return Response(RendimientoSerializer(nuevo).data, status=201)

@api_view(['GET', 'PUT', 'DELETE'])
def api_rendimiento_detail(request, pk):
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
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {
                    "type": "nuevo_rendimiento",
                    "data": serializer.data
                }
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        rendimiento.delete()
        # Puedes enviar notificación si quieres
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_rendimiento_stats(request):
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
