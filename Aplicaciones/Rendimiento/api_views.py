# Rendimiento/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
import json
from .models import JornadaLaboral
from .serializers import JornadaLaboralSerializer

@csrf_exempt
def iniciar_jornada_api(request):
    """
    API para iniciar jornada laboral desde Flutter
    POST: http://localhost:8000/api/jornada/iniciar/
    """
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "Método no permitido. Use POST"
        }, status=405)
    
    try:
        # 1. Obtener y validar JSON
        data = json.loads(request.body.decode("utf-8"))
        
        # 2. Validar campos requeridos
        usuario_username = data.get('usuario_username', '').strip()
        usuario_nombre = data.get('usuario_nombre', '').strip()
        mesa = data.get('mesa', '').strip()
        
        if not usuario_username:
            return JsonResponse({
                "success": False,
                "error": "El username del usuario es requerido"
            }, status=400)
        
        if not mesa:
            return JsonResponse({
                "success": False,
                "error": "La mesa es requerida"
            }, status=400)
        
        # 3. Verificar si ya tiene una jornada activa hoy
        hoy = timezone.localdate()
        jornada_activa = JornadaLaboral.objects.filter(
            usuario_username=usuario_username,
            fecha=hoy,
            estado='iniciada'
        ).first()
        
        if jornada_activa:
            return JsonResponse({
                "success": False,
                "error": "Ya tienes una jornada iniciada hoy",
                "jornada_actual": JornadaLaboralSerializer(jornada_activa).data
            }, status=400)
        
        # 4. Crear nueva jornada
        jornada = JornadaLaboral.objects.create(
            usuario_username=usuario_username,
            usuario_nombre=usuario_nombre,
            mesa=mesa,
            hora_inicio=timezone.now()
        )
        
        # 5. Respuesta exitosa
        return JsonResponse({
            "success": True,
            "message": "Jornada iniciada exitosamente",
            "data": JornadaLaboralSerializer(jornada).data
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "JSON inválido en el cuerpo de la solicitud"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error del servidor: {str(e)}"
        }, status=500)

@csrf_exempt
def finalizar_jornada_api(request):
    """
    API para finalizar jornada laboral desde Flutter
    POST: http://localhost:8000/api/jornada/finalizar/
    """
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "Método no permitido. Use POST"
        }, status=405)
    
    try:
        # 1. Obtener y validar JSON
        data = json.loads(request.body.decode("utf-8"))
        
        # 2. Validar campos requeridos
        usuario_username = data.get('usuario_username', '').strip()
        
        if not usuario_username:
            return JsonResponse({
                "success": False,
                "error": "El username del usuario es requerido"
            }, status=400)
        
        # 3. Verificar si tiene una jornada activa hoy
        hoy = timezone.localdate()
        jornada_activa = JornadaLaboral.objects.filter(
            usuario_username=usuario_username,
            fecha=hoy,
            estado='iniciada'
        ).first()
        
        if not jornada_activa:
            return JsonResponse({
                "success": False,
                "error": "No tienes una jornada iniciada hoy"
            }, status=400)
        
        # 4. Finalizar la jornada
        jornada_activa.hora_fin = timezone.now()
        jornada_activa.save()  # El save() ya calcula las horas y cambia el estado
        
        # 5. Respuesta exitosa
        return JsonResponse({
            "success": True,
            "message": "Jornada finalizada exitosamente",
            "data": JornadaLaboralSerializer(jornada_activa).data
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "JSON inválido en el cuerpo de la solicitud"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error del servidor: {str(e)}"
        }, status=500)

@csrf_exempt
def obtener_jornada_actual_api(request):
    """
    API para obtener la jornada actual del usuario
    GET: http://localhost:8000/api/jornada/actual/?usuario_username=juan
    """
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "error": "Método no permitido. Use GET"
        }, status=405)
    
    try:
        # 1. Obtener parámetros
        usuario_username = request.GET.get('usuario_username')
        
        if not usuario_username:
            return JsonResponse({
                "success": False,
                "error": "El parámetro 'usuario_username' es requerido"
            }, status=400)
        
        # 2. Buscar jornada activa hoy
        hoy = timezone.localdate()
        jornada_activa = JornadaLaboral.objects.filter(
            usuario_username=usuario_username,
            fecha=hoy,
            estado='iniciada'
        ).first()
        
        # 3. Buscar última jornada (si no hay activa)
        ultima_jornada = JornadaLaboral.objects.filter(
            usuario_username=usuario_username
        ).order_by('-fecha', '-hora_inicio').first()
        
        # 4. Preparar respuesta
        response_data = {
            "tiene_jornada_activa": jornada_activa is not None,
            "jornada_activa": JornadaLaboralSerializer(jornada_activa).data if jornada_activa else None,
            "ultima_jornada": JornadaLaboralSerializer(ultima_jornada).data if ultima_jornada else None
        }
        
        return JsonResponse({
            "success": True,
            "data": response_data
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error del servidor: {str(e)}"
        }, status=500)

@csrf_exempt
def obtener_historial_jornadas_api(request):
    """
    API para obtener historial de jornadas del usuario
    GET: http://localhost:8000/api/jornada/historial/?usuario_username=juan&limit=10
    """
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "error": "Método no permitido. Use GET"
        }, status=405)
    
    try:
        # 1. Obtener parámetros
        usuario_username = request.GET.get('usuario_username')
        limit = int(request.GET.get('limit', 30))
        
        if not usuario_username:
            return JsonResponse({
                "success": False,
                "error": "El parámetro 'usuario_username' es requerido"
            }, status=400)
        
        # 2. Obtener jornadas ordenadas por fecha descendente
        jornadas = JornadaLaboral.objects.filter(
            usuario_username=usuario_username
        ).order_by('-fecha', '-hora_inicio')[:limit]
        
        # 3. Calcular estadísticas
        total_jornadas = jornadas.count()
        total_horas = sum(j.horas_trabajadas or 0 for j in jornadas if j.horas_trabajadas)
        
        # 4. Preparar respuesta
        return JsonResponse({
            "success": True,
            "data": {
                "total_jornadas": total_jornadas,
                "total_horas": round(total_horas, 2),
                "jornadas": JornadaLaboralSerializer(jornadas, many=True).data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error del servidor: {str(e)}"
        }, status=500)