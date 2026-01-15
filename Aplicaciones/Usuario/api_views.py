# api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
import json
from .models import Usuario, Mesa  # Asegúrate de importar Mesa también

@csrf_exempt
def registrar_usuario_api(request):
    """
    API para registro desde Flutter
    POST: http://localhost:8000/api/registrar/
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
        campos_requeridos = ['nombres', 'apellidos', 'mesa', 'cargo', 'username', 'password']
        campos_faltantes = []
        
        for campo in campos_requeridos:
            if campo not in data or not str(data[campo]).strip():
                campos_faltantes.append(campo)
        
        if campos_faltantes:
            return JsonResponse({
                "success": False,
                "error": f"Campos requeridos faltantes: {', '.join(campos_faltantes)}"
            }, status=400)
        
        # 3. Verificar si usuario ya existe
        username = data['username'].strip()
        if Usuario.objects.filter(username=username).exists():
            return JsonResponse({
                "success": False,
                "error": f"El usuario '{username}' ya existe"
            }, status=400)
        
        # 4. Crear usuario con contraseña hasheada
        usuario = Usuario(
            nombres=data['nombres'].strip(),
            apellidos=data['apellidos'].strip(),
            mesa=data['mesa'].strip(),
            cargo=data['cargo'].strip(),
            username=username
        )
        usuario.password = make_password(data['password'].strip())
        usuario.save()
        
        # 5. Respuesta exitosa
        return JsonResponse({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "data": {
                "id": usuario.id,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "mesa": usuario.mesa,
                "cargo": usuario.cargo,
                "username": usuario.username
            }
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
def login_usuario_api(request):
    """
    API para login desde Flutter
    POST: http://localhost:8000/api/login/
    """
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "Método no permitido. Use POST"
        }, status=405)
    
    try:
        # 1. Obtener datos
        data = json.loads(request.body.decode("utf-8"))
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return JsonResponse({
                "success": False,
                "error": "Usuario y contraseña son requeridos"
            }, status=400)
        
        # 2. Credenciales de admin (hardcodeado como en tu views.py)
        if username == "comexad" and password == "Comexiger2025":
            return JsonResponse({
                "success": True,
                "message": "Login exitoso como administrador",
                "data": {
                    "username": username,
                    "tipo": "admin",
                    "nombres": "Administrador",
                    "apellidos": "System"
                }
            })
        
        # 3. Buscar usuario en base de datos
        try:
            usuario = Usuario.objects.get(username=username)
            
            # 4. Verificar contraseña
            from django.contrib.auth.hashers import check_password
            if check_password(password, usuario.password):
                return JsonResponse({
                    "success": True,
                    "message": "Login exitoso",
                    "data": {
                        "id": usuario.id,
                        "nombres": usuario.nombres,
                        "apellidos": usuario.apellidos,
                        "mesa": usuario.mesa,
                        "cargo": usuario.cargo,
                        "username": usuario.username,
                        "tipo": "usuario"
                    }
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "Credenciales incorrectas"
                }, status=401)
                
        except Usuario.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Usuario no encontrado"
            }, status=404)
            
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
def obtener_mesas_api(request):
    """
    API para obtener todas las mesas registradas
    GET: http://localhost:8000/api/mesas/
    """
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "error": "Método no permitido. Use GET"
        }, status=405)
    
    try:
        # Obtener todas las mesas ordenadas por nombre
        mesas = Mesa.objects.all().order_by('nombre')
        
        # Convertir a lista de diccionarios
        mesas_list = []
        for mesa in mesas:
            mesas_list.append({
                "id": mesa.id,
                "nombre": mesa.nombre
            })
        
        return JsonResponse({
            "success": True,
            "data": mesas_list,
            "count": len(mesas_list)
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error del servidor: {str(e)}"
        }, status=500)

@csrf_exempt
def verificar_mesa_api(request):
    """
    API para verificar si una mesa existe
    POST: http://localhost:8000/api/verificar_mesa/
    """
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "error": "Método no permitido. Use POST"
        }, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        nombre_mesa = data.get('nombre', '').strip()
        
        if not nombre_mesa:
            return JsonResponse({
                "success": False,
                "error": "El nombre de la mesa es requerido"
            }, status=400)
        
        existe = Mesa.objects.filter(nombre__iexact=nombre_mesa).exists()
        
        return JsonResponse({
            "success": True,
            "existe": existe,
            "nombre": nombre_mesa
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "JSON inválido"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error del servidor: {str(e)}"
        }, status=500)