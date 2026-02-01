from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .jwt_utils import decodificar_token, crear_access_token

@csrf_exempt
def refresh_token_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido. Use POST"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        refresh = (data.get("refresh") or "").strip()

        if not refresh:
            return JsonResponse({"success": False, "error": "Falta refresh token"}, status=400)



        try:
            payload = decodificar_token(refresh)
        except Exception as e:
            print(" ERROR DECODIFICAR REFRESH:", repr(e))
            return JsonResponse({"success": False, "error": "Refresh inválido o expirado"}, status=401)

        if payload.get("type") != "refresh":
            return JsonResponse({"success": False, "error": "Token incorrecto (se requiere refresh)"}, status=401)

        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            return JsonResponse({"success": False, "error": "Refresh sin sub/user_id"}, status=401)

        new_access = crear_access_token({"sub": str(user_id), "type": "access"}, minutes=60)

        return JsonResponse({"success": True, "access": new_access}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"}, status=400)
    except Exception as e:
        print("ERROR GENERAL REFRESH:", repr(e))
        return JsonResponse({"success": False, "error": f"Error del servidor: {str(e)}"}, status=500)
