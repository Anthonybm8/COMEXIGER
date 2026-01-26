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


from Aplicaciones.Usuario.web_decorators import web_login_required

# ================== VISTAS WEB ==================
@web_login_required
def inicio(request):
    # ✅ Mostrar solo jornadas base (opcional pero recomendado)
    listadoRendimiento = Rendimiento.objects.filter(qr_id="JORNADA").order_by('-fecha_entrada')
    return render(request, 'rendimiento.html', {'rendimiento': listadoRendimiento})

@web_login_required
def nuevo_rendimiento(request):
    return render(request, "nuevo_rendimiento.html")

@web_login_required
def guardar_rendimiento(request):
    """
    Manual (web). Si no lo usas, puedes eliminar esta vista.
    """
    if request.method == "POST":
        try:
            numero_mesa = request.POST["numero_mesa"]
            fecha_entrada_str = request.POST.get("fecha_entrada")
            bonches = int(request.POST.get("bonches", 0))

            if fecha_entrada_str:
                try:
                    fecha_entrada_dt = datetime.strptime(fecha_entrada_str, "%Y-%m-%dT%H:%M")
                    fecha_entrada_dt = timezone.make_aware(
                        fecha_entrada_dt, timezone.get_current_timezone()
                    )
                except Exception:
                    fecha_entrada_dt = timezone.now()
            else:
                fecha_entrada_dt = timezone.now()

            nuevo = Rendimiento.objects.create(
                qr_id="MANUAL",
                numero_mesa=numero_mesa,
                fecha_entrada=fecha_entrada_dt,
                bonches=bonches
            )

            nuevo.recalcular()
            nuevo.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {"type": "nuevo_rendimiento", "data": RendimientoSerializer(nuevo).data}
            )

            messages.success(request, "Rendimiento guardado exitosamente")
            return redirect('rendimiento')

        except Exception as e:
            messages.error(request, f"Error al guardar rendimiento: {e}")
            return redirect('nuevo_rendimiento')

    messages.error(request, "Error al guardar rendimiento")
    return redirect('nuevo_rendimiento')

@web_login_required
def eliminar_rendimiento(request, id):
    rendimiento_eliminar = Rendimiento.objects.get(id=id)
    rendimiento_eliminar.delete()
    messages.success(request, "Rendimiento eliminado exitosamente")
    return redirect('rendimiento')

@web_login_required
def procesar_edicion_rendimiento(request):
    if request.method == "POST":
        try:
            rendimiento = Rendimiento.objects.get(id=request.POST["id"])

            rendimiento.numero_mesa = request.POST["numero_mesa"]
            rendimiento.bonches = int(request.POST.get("bonches", 0))
            # ✅ SI editas rendimiento desde el modal, guárdalo
            if request.POST.get("rendimiento"):
                rendimiento.rendimiento = int(request.POST.get("rendimiento"))

            if request.POST.get("fecha_entrada"):
                try:
                    dt = datetime.strptime(request.POST["fecha_entrada"], "%Y-%m-%dT%H:%M")
                    rendimiento.fecha_entrada = timezone.make_aware(
                        dt, timezone.get_current_timezone()
                    )
                except Exception:
                    pass

            if request.POST.get("hora_inicio"):
                try:
                    dt = datetime.strptime(request.POST["hora_inicio"], "%Y-%m-%dT%H:%M")
                    rendimiento.hora_inicio = timezone.make_aware(
                        dt, timezone.get_current_timezone()
                    )
                except Exception:
                    pass

            if request.POST.get("hora_final"):
                try:
                    dt = datetime.strptime(request.POST["hora_final"], "%Y-%m-%dT%H:%M")
                    rendimiento.hora_final = timezone.make_aware(
                        dt, timezone.get_current_timezone()
                    )
                except Exception:
                    pass

            rendimiento.recalcular()
            rendimiento.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {"type": "nuevo_rendimiento", "data": RendimientoSerializer(rendimiento).data}
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
            Rendimiento.objects.filter(qr_id="JORNADA", hora_final__isnull=True).order_by('-fecha_entrada'),
            many=True
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_mesa(self, request):
        mesa = request.query_params.get('mesa')
        if not mesa:
            return Response({"error": "Parámetro 'mesa' requerido"}, status=400)

        serializer = self.get_serializer(
            Rendimiento.objects.filter(qr_id="JORNADA", numero_mesa=mesa).order_by('-fecha_entrada'),
            many=True
        )
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def api_rendimiento_list(request):
    # ---------- GET ----------
    if request.method == 'GET':
        rendimientos = Rendimiento.objects.filter(qr_id="JORNADA")

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
            campo = {"mesa": "numero_mesa", "fecha": "fecha_entrada"}.get(ordenar)
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

    if not codigo or not mesa:
        return Response({"error": "Datos incompletos"}, status=status.HTTP_400_BAD_REQUEST)

    hoy = timezone.localdate()

    # ✅ 0) Debe existir jornada activa para esa mesa hoy
    jornada_base = (Rendimiento.objects
        .filter(qr_id="JORNADA", numero_mesa=mesa, hora_final__isnull=True)
        .order_by("-hora_inicio", "-fecha_entrada")
        .first()
    )


    if not jornada_base:
        return Response(
            {"error": "No hay jornada iniciada para esta mesa hoy. Primero inicia jornada."},
            status=status.HTTP_409_CONFLICT
        )

    # 🔒 1) QR no repetido para siempre
    if QRUsado.objects.filter(qr_id=codigo).exists():
        return Response({"error": "Este QR ya fue utilizado"}, status=status.HTTP_409_CONFLICT)

    QRUsado.objects.create(qr_id=codigo)

    # ✅ 2) Sumar al registro base
    jornada_base.bonches += 1
    jornada_base.recalcular()
    jornada_base.save()

    # ✅ websocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "rendimientos",
        {"type": "nuevo_rendimiento", "data": RendimientoSerializer(jornada_base).data}
    )

    return Response(RendimientoSerializer(jornada_base).data, status=200)


@api_view(['GET', 'PUT', 'DELETE'])
def api_rendimiento_detail(request, pk):
    try:
        rendimiento = Rendimiento.objects.get(pk=pk)
    except Rendimiento.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(RendimientoSerializer(rendimiento).data)

    if request.method == 'PUT':
        serializer = RendimientoSerializer(rendimiento, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()   # guarda los campos enviados
            obj.recalcular()          # recalcula con hora_inicio/hora_final
            obj.save()                # guarda los calculados

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "rendimientos",
                {"type": "nuevo_rendimiento", "data": RendimientoSerializer(obj).data}
            )

            return Response(RendimientoSerializer(obj).data)

        return Response(serializer.errors, status=400)



@api_view(['GET'])
def api_rendimiento_stats(request):
    jornadas = Rendimiento.objects.filter(qr_id="JORNADA")
    return Response({
        'total_rendimientos': jornadas.count(),
        'rendimientos_activos': jornadas.filter(hora_final__isnull=True).count(),
        'total_bonches': jornadas.aggregate(Sum('bonches'))['bonches__sum'] or 0,
        'mesas_activas': jornadas.filter(hora_final__isnull=True).values('numero_mesa').distinct().count()
    })
