# Rendimiento/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from Aplicaciones.Usuario.jwt_decorators import jwt_required
from .models import Rendimiento
from .serializers import RendimientoSerializer

def _broadcast_rendimiento(rendimiento):
    channel_layer = get_channel_layer()

    data = RendimientoSerializer(rendimiento).data

    # ✅ opcional: asegurar que hora_inicio/hora_final salgan como "HH:MM"
    # si serializer te devuelve "02:06:03" está bien, en front cortamos a HH:MM
    async_to_sync(channel_layer.group_send)(
        "rendimientos",
        {
            "type": "nuevo_rendimiento",  # 👈 debe coincidir con tu consumer
            "data": data
        }
    )

@csrf_exempt
@jwt_required
def iniciar_jornada_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido. Use POST"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        mesa = (data.get("mesa") or data.get("numero_mesa") or "").strip()
        if not mesa:
            return JsonResponse({"success": False, "error": "La mesa es requerida"}, status=400)

        rendimiento_val = int(data.get("rendimiento") or 20)
        ramos_base_val  = int(data.get("ramos_base") or 0)

        # ✅ NO depender de "hoy": buscar jornada activa real
        jornada_activa = (Rendimiento.objects
            .filter(qr_id="JORNADA", numero_mesa=mesa, hora_final__isnull=True)
            .order_by("-hora_inicio", "-fecha_entrada")
            .first()
        )

        if jornada_activa:
            return JsonResponse({
                "success": False,
                "error": "Ya existe una jornada activa para esta mesa",
                "data": RendimientoSerializer(jornada_activa).data
            }, status=409)

        r = Rendimiento.objects.create(
            qr_id="JORNADA",
            numero_mesa=mesa,
            fecha_entrada=timezone.now(),
            hora_inicio=timezone.now(),
            hora_final=None,
            rendimiento=20,   
            bonches=0
        )


        r.save()  # (si tu modelo recalcula en save)
        _broadcast_rendimiento(r)

        return JsonResponse({
            "success": True,
            "message": "Jornada iniciada exitosamente",
            "data": RendimientoSerializer(r).data
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@csrf_exempt
@jwt_required
def finalizar_jornada_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido. Use POST"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        mesa = (data.get("mesa") or data.get("numero_mesa") or "").strip()
        if not mesa:
            return JsonResponse({"success": False, "error": "La mesa es requerida"}, status=400)

        jornada_activa = (Rendimiento.objects
            .filter(qr_id="JORNADA", numero_mesa=mesa, hora_final__isnull=True)
            .order_by("-hora_inicio", "-fecha_entrada")
            .first()
        )

        if not jornada_activa:
            return JsonResponse({"success": False, "error": "No hay jornada activa para esta mesa"}, status=404)

        jornada_activa.hora_final = timezone.now()
        jornada_activa.save()  # (recalcula en save)
        _broadcast_rendimiento(jornada_activa)

        return JsonResponse({
            "success": True,
            "message": "Jornada finalizada exitosamente",
            "data": RendimientoSerializer(jornada_activa).data
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@csrf_exempt
@jwt_required
def obtener_jornada_actual_api(request):
    """
    GET: /api/jornada/actual/?mesa=1
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "Método no permitido. Use GET"}, status=405)

    try:
        mesa = (request.GET.get("mesa") or request.GET.get("numero_mesa") or "").strip()
        if not mesa:
            return JsonResponse({"success": False, "error": "El parámetro 'mesa' es requerido"}, status=400)

        hoy = timezone.localdate()

        jornada_activa = Rendimiento.objects.filter(
            qr_id="JORNADA",
            numero_mesa=mesa,
            fecha_entrada__date=hoy,
            hora_final__isnull=True
        ).order_by("-fecha_entrada").first()

        ultima_jornada = Rendimiento.objects.filter(
            qr_id="JORNADA",
            numero_mesa=mesa
        ).order_by("-fecha_entrada").first()

        return JsonResponse({
            "success": True,
            "data": {
                "tiene_jornada_activa": jornada_activa is not None,
                "jornada_activa": RendimientoSerializer(jornada_activa).data if jornada_activa else None,
                "ultima_jornada": RendimientoSerializer(ultima_jornada).data if ultima_jornada else None
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@jwt_required
def obtener_historial_jornadas_api(request):
    """
    GET: /api/jornada/historial/?mesa=1&limit=30
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "Método no permitido. Use GET"}, status=405)

    try:
        mesa = (request.GET.get("mesa") or request.GET.get("numero_mesa") or "").strip()
        limit = int(request.GET.get("limit", 30))

        if not mesa:
            return JsonResponse({"success": False, "error": "El parámetro 'mesa' es requerido"}, status=400)

        jornadas = Rendimiento.objects.filter(
            qr_id="JORNADA",
            numero_mesa=mesa
        ).order_by("-fecha_entrada")[:limit]

        total_horas = sum((j.horas_trabajadas or 0) for j in jornadas)

        return JsonResponse({
            "success": True,
            "data": {
                "total_jornadas": jornadas.count(),
                "total_horas": round(total_horas, 2),
                "jornadas": RendimientoSerializer(jornadas, many=True).data
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
