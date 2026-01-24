from functools import wraps
from django.http import JsonResponse
from .jwt_utils import decodificar_token
from .models import Usuario

def jwt_required(view_func):
    """
    Requiere header:
      Authorization: Bearer <access_token>

    Inyecta request.api_user (Usuario) o request.api_admin=True si fuera admin.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth:
            return JsonResponse({"success": False, "error": "Falta Authorization: Bearer <token>"}, status=401)

        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JsonResponse({"success": False, "error": "Formato Authorization inválido (usa Bearer <token>)"}, status=401)

        token = parts[1].strip()

        try:
            payload = decodificar_token(token)
        except Exception:
            return JsonResponse({"success": False, "error": "Token inválido o expirado"}, status=401)

        if payload.get("type") != "access":
            return JsonResponse({"success": False, "error": "Token incorrecto (se requiere access token)"}, status=401)

        # (opcional) admin si lo usas
        if payload.get("tipo") == "admin":
            request.api_admin = True
            request.api_user = None
            return view_func(request, *args, **kwargs)

        # ✅ Usuario normal: usamos "sub" (nuevo)
        user_id = payload.get("sub") or payload.get("user_id")  # compatibilidad
        if not user_id:
            return JsonResponse({"success": False, "error": "Token sin sub/user_id"}, status=401)

        try:
            request.api_user = Usuario.objects.get(id=int(user_id))
            request.api_admin = False
        except Usuario.DoesNotExist:
            return JsonResponse({"success": False, "error": "Usuario no existe"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped
