from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.utils import timezone

from .models import Rendimiento, QRUsado
from .serializers import RendimientoSerializer

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response


# ================== VISTAS WEB ==================

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

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "rendimientos",
            {
                "type": "nuevo_rendimiento",
                "data": RendimientoSerializer(nuevo).data
            }
        )

        messages.success(request, "Rendimiento guardado exitosamente")
        return redirect('rendimiento')

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
            rendimiento = Rendimiento.objects.get(id=request.POST["id"])

            rendimiento.numero_mesa = request.POST["numero_mesa"]
            rendimiento.variedad = request.POST["variedad"]
            rendimiento.medida = request.POST["medida"]
            rendimiento.bonches = int(request.POST["bonches"])

            if request.POST.get("fecha_entrada"):
                rendimiento.fecha_entrada = datetime.strptime(
                    request.POST["fecha_entrada"], "%Y-%m-%dT%H:%M"
                )

            if request.POST.get("fecha_salida"):
                rendimiento.fecha_salida = datetime.strptime(
                    request.POST["fecha_salida"], "%Y-%m-%dT%H:%M"
                )
            else:
                rendimiento.fecha_salida = None

            rendimiento.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {
                    "type": "nuevo_rendimiento",
                    "data": RendimientoSerializer(rendimiento).data
                }
            )

            messages.success(request, "Rendimiento actualizado correctamente")

        except Exception as e:
            messages.error(request, f"Error al procesar la edición: {e}")

        return redirect('rendimiento')


# ================== API REST ==================

class RendimientoViewSet(viewsets.ModelViewSet):
    queryset = Rendimiento.objects.all().order_by('-fecha_entrada')
    serializer_class = RendimientoSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        serializer = self.get_serializer(
            Rendimiento.objects.filter(fecha_salida__isnull=True),
            many=True
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_mesa(self, request):
        mesa = request.query_params.get('mesa')
        if not mesa:
            return Response({"error": "Parámetro 'mesa' requerido"}, status=400)

        serializer = self.get_serializer(
            Rendimiento.objects.filter(numero_mesa=mesa),
            many=True
        )
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def api_rendimiento_list(request):

    # ---------- GET ----------
    if request.method == 'GET':
        rendimientos = Rendimiento.objects.all()

        if request.query_params.get("fecha"):
            rendimientos = rendimientos.filter(
                fecha_entrada__date=request.query_params["fecha"]
            )

        if request.query_params.get("desde") and request.query_params.get("hasta"):
            rendimientos = rendimientos.filter(
                fecha_entrada__date__range=[
                    request.query_params["desde"],
                    request.query_params["hasta"]
                ]
            )

        ordenar = request.query_params.get("ordenar")
        reciente = request.query_params.get("reciente")

        if ordenar:
            campo = {
                "mesa": "numero_mesa",
                "variedad": "variedad",
                "medida": "medida",
                "fecha": "fecha_entrada"
            }.get(ordenar)

            if campo:
                if reciente == "true":
                    campo = f"-{campo}"
                rendimientos = rendimientos.order_by(campo)

        serializer = RendimientoSerializer(rendimientos, many=True)
        return Response(serializer.data)

    # ---------- POST (QR) ----------
    data = request.data

    codigo = data.get("qr_id")
    mesa = data.get("numero_mesa")
    variedad = data.get("variedad")
    medida = data.get("medida")

    if not codigo or not mesa or not variedad or not medida:
        return Response(
            {"error": "Datos incompletos"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔒 BLOQUEO PERMANENTE
    if QRUsado.objects.filter(qr_id=codigo).exists():
        return Response(
            {"error": "Este QR ya fue utilizado"},
            status=status.HTTP_409_CONFLICT
        )

    # Guardar QR como usado PARA SIEMPRE
    QRUsado.objects.create(qr_id=codigo)

    hoy = timezone.localdate()

    existente = Rendimiento.objects.filter(
        numero_mesa=mesa,
        variedad=variedad,
        medida=medida,
        fecha_entrada__date=hoy
    ).first()

    if existente:
        existente.bonches += 1
        existente.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "rendimientos",
            {
                "type": "nuevo_rendimiento",
                "data": RendimientoSerializer(existente).data
            }
        )

        return Response(RendimientoSerializer(existente).data, status=200)

    nuevo = Rendimiento.objects.create(
        qr_id=codigo,
        numero_mesa=mesa,
        variedad=variedad,
        medida=medida,
        bonches=1,
        fecha_entrada=timezone.now()
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "rendimientos",
        {
            "type": "nuevo_rendimiento",
            "data": RendimientoSerializer(nuevo).data
        }
    )

    return Response(
        RendimientoSerializer(nuevo).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET', 'PUT', 'DELETE'])
def api_rendimiento_detail(request, pk):
    try:
        rendimiento = Rendimiento.objects.get(pk=pk)
    except Rendimiento.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(RendimientoSerializer(rendimiento).data)

    if request.method == 'PUT':
        serializer = RendimientoSerializer(rendimiento, data=request.data)
        if serializer.is_valid():
            serializer.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {
                    "type": "nuevo_rendimiento",
                    "data": serializer.data
                }
            )

            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    rendimiento.delete()
    return Response(status=204)


@api_view(['GET'])
def api_rendimiento_stats(request):
    return Response({
        'total_rendimientos': Rendimiento.objects.count(),
        'rendimientos_activos': Rendimiento.objects.filter(
            fecha_salida__isnull=True
        ).count(),
        'total_bonches': Rendimiento.objects.aggregate(
            Sum('bonches')
        )['bonches__sum'] or 0,
        'mesas_activas': Rendimiento.objects.filter(
            fecha_salida__isnull=True
        ).values('numero_mesa').distinct().count()
    })
