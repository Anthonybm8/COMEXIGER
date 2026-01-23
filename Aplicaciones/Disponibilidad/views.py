from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import Disponibilidad
from .serializers import DisponibilidadSerializer
from .models import Disponibilidad, QRDisponibilidadUsado



def inicio(request):
   
    disponibilidades = Disponibilidad.objects.all()
    return render(request, 'disponibilidad.html', {
        'disponibilidades': disponibilidades
    })



def eliminar_disponibilidad(request, id):
    Disponibilidad.objects.get(id=id).delete()
    messages.success(request, "Disponibilidad eliminada correctamente")
    return redirect('dispo')


def procesar_edicion_disponibilidad(request):
    if request.method == "POST":
        try:
            d = Disponibilidad.objects.get(id=request.POST["id"])

            d.numero_mesa = request.POST["numero_mesa"]
            d.variedad = request.POST["variedad"]
            d.medida = request.POST["medida"]
            d.stock = int(request.POST["stock"])

            if request.POST.get("fecha_entrada"):
                d.fecha_entrada = datetime.strptime(
                    request.POST["fecha_entrada"], "%Y-%m-%dT%H:%M"
                )

            if request.POST.get("fecha_salida"):
                d.fecha_salida = datetime.strptime(
                    request.POST["fecha_salida"], "%Y-%m-%dT%H:%M"
                )
            else:
                d.fecha_salida = None

            d.save()

            async_to_sync(get_channel_layer().group_send)(
                "disponibilidad",
                {
                    "type": "nueva_disponibilidad",
                    "data": DisponibilidadSerializer(d).data
                }
            )

            messages.success(request, "Disponibilidad actualizada correctamente")

        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('dispo')


# =========================
# API REST – VIEWSET
# =========================

class DisponibilidadViewSet(viewsets.ModelViewSet):
    queryset = Disponibilidad.objects.all().order_by('-fecha_entrada')
    serializer_class = DisponibilidadSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        qs = Disponibilidad.objects.filter(fecha_salida__isnull=True)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def por_mesa(self, request):
        mesa = request.query_params.get("mesa")
        if not mesa:
            return Response({"error": "Parámetro mesa requerido"}, status=400)
        qs = Disponibilidad.objects.filter(numero_mesa=mesa)
        return Response(self.get_serializer(qs, many=True).data)


# =========================
# API MANUAL
# =========================
@api_view(['GET', 'POST'])
def api_disponibilidad_list(request):

    if request.method == 'GET':
        ordenar = request.query_params.get("ordenar")
        fecha = request.query_params.get("fecha")
        desde = request.query_params.get("desde")
        hasta = request.query_params.get("hasta")
        reciente = request.query_params.get("reciente")
        
        qs = Disponibilidad.objects.all()
        
        if fecha:
            qs = qs.filter(fecha_entrada__date=fecha)

        if desde and hasta:
            qs = qs.filter(fecha_entrada__date__range=[desde, hasta])

        campos = {
            "mesa": "numero_mesa",
            "variedad": "variedad",
            "medida": "medida",
            "fecha": "fecha_entrada"
        }

        if ordenar in campos:
            campo = campos[ordenar]
            if reciente == "true":
                campo = "-" + campo
            qs = qs.order_by(campo)
        
        return Response(DisponibilidadSerializer(qs, many=True).data)

    elif request.method == 'POST':

        data = request.data
        codigo = data.get("qr_id")
        mesa = data.get("numero_mesa")
        variedad = data.get("variedad")
        medida = data.get("medida")

        if not codigo or not mesa or not variedad or not medida:
            return Response({"error": "Datos incompletos"}, status=status.HTTP_400_BAD_REQUEST)


        if QRDisponibilidadUsado.objects.filter(qr_id=codigo).exists():
            return Response(
                {"error": "Este QR ya fue utilizado en Disponibilidad"},
                status=status.HTTP_409_CONFLICT
            )

        # Guardar QR para siempre
        QRDisponibilidadUsado.objects.create(qr_id=codigo)

        hoy = timezone.localdate()

        existente = Disponibilidad.objects.filter(
            numero_mesa=mesa,
            variedad=variedad,
            medida=medida,
            fecha_entrada__date=hoy
        ).first()

        if existente:
            existente.stock += 1
            existente.save()

            async_to_sync(get_channel_layer().group_send)(
                "disponibilidad",
                {
                    "type": "nueva_disponibilidad",
                    "data": DisponibilidadSerializer(existente).data
                }
            )
            return Response(DisponibilidadSerializer(existente).data, status=200)

        nuevo = Disponibilidad.objects.create(
            numero_mesa=mesa,
            variedad=variedad,
            medida=medida,
            stock=1,
            fecha_entrada=timezone.now()
        )

        async_to_sync(get_channel_layer().group_send)(
            "disponibilidad",
            {
                "type": "nueva_disponibilidad",
                "data": DisponibilidadSerializer(nuevo).data
            }
        )

        return Response(DisponibilidadSerializer(nuevo).data, status=201)


@api_view(['GET', 'PUT', 'DELETE'])
def api_disponibilidad_detail(request, pk):
    try:
        disponibilidad = Disponibilidad.objects.get(pk=pk)
    except Disponibilidad.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DisponibilidadSerializer(disponibilidad)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DisponibilidadSerializer(disponibilidad, data=request.data)
        if serializer.is_valid():
            serializer.save()

            async_to_sync(get_channel_layer().group_send)(
                "disponibilidad",
                {
                    "type": "nueva_disponibilidad",
                    "data": serializer.data
                }
            )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        disponibilidad.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_disponibilidad_stats(request):
    return Response({
        "total_registros": Disponibilidad.objects.count(),
        "registros_activos": Disponibilidad.objects.filter(fecha_salida__isnull=True).count(),
        "stock_total": Disponibilidad.objects.aggregate(Sum('stock'))['stock__sum'] or 0,
        "mesas_activas": Disponibilidad.objects.filter(fecha_salida__isnull=True)
                            .values('numero_mesa')
                            .distinct()
                            .count()
    })
#API PARA LA DISPONIBILIDAD QUE SALE
from .models import Disponibilidad, QRDisponibilidadSalidaUsado

@api_view(['POST'])
def api_disponibilidad_salida(request):
    data = request.data
    codigo = data.get("qr_id")
    variedad = data.get("variedad")
    medida = data.get("medida")

    if not codigo or not variedad or not medida:
        return Response(
            {"error": "Datos incompletos: qr_id, variedad y medida son obligatorios"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ⛔ Si ya se restó este QR una vez, NO permitir otra vez
    if QRDisponibilidadSalidaUsado.objects.filter(qr_id=codigo).exists():
        return Response(
            {"error": "Este QR ya fue utilizado en SALIDA (ya se restó una vez)"},
            status=status.HTTP_409_CONFLICT
        )

    channel_layer = get_channel_layer()

    with transaction.atomic():
        dispo = (Disponibilidad.objects
                 .select_for_update()
                 .filter(
                     fecha_salida__isnull=True,
                     variedad=variedad,
                     medida=medida,
                     stock__gt=0
                 )
                 .order_by('fecha_entrada', 'id')
                 .first())

        if not dispo:
            return Response(
                {"error": "No hay stock disponible para esa variedad y medida"},
                status=status.HTTP_409_CONFLICT
            )

        # Registrar QR como ya restado
        QRDisponibilidadSalidaUsado.objects.create(qr_id=codigo)

        # Restar 1
        dispo.stock -= 1

        # Si llega a 0, marca fecha_salida (opcional)
        if dispo.stock == 0:
            dispo.fecha_salida = timezone.now()

        dispo.save()

    # Notificar por websocket
    async_to_sync(channel_layer.group_send)(
        "disponibilidad",
        {
            "type": "nueva_disponibilidad",
            "data": DisponibilidadSerializer(dispo).data
        }
    )

    return Response(DisponibilidadSerializer(dispo).data, status=status.HTTP_200_OK)