# Aplicaciones/Usuario/jwt_decorators.py

from functools import wraps
from django.http import JsonResponse
from Aplicaciones.Usuario.jwt_utils import decodificar_token
from Aplicaciones.Usuario.models import Usuario

def jwt_required(view_func=None, *, allowed_cargos=None, enforce_mesa=False):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            auth = request.headers.get("Authorization", "")

            if not auth:
                return JsonResponse({"success": False, "error": "Token requerido"}, status=401)

            parts = auth.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return JsonResponse(
                    {"success": False, "error": "Formato Authorization inválido. Usa: Bearer <token>"},
                    status=401
                )

            token = parts[1].strip()

            try:
                payload = decodificar_token(token)
            except Exception:
                return JsonResponse({"success": False, "error": "Token inválido o expirado"}, status=401)

            if payload.get("type") != "access":
                return JsonResponse({"success": False, "error": "Token incorrecto (se requiere access token)"}, status=401)

            usuario_id = payload.get("sub")
            if not usuario_id:
                return JsonResponse({"success": False, "error": "Token sin 'sub'"}, status=401)

            try:
                usuario = Usuario.objects.get(id=int(usuario_id))
            except Usuario.DoesNotExist:
                return JsonResponse({"success": False, "error": "Usuario no existe"}, status=401)


            request.usuario = usuario
            request.jwt_payload = payload


            if allowed_cargos:
                cargo_user = (usuario.cargo or "").strip().upper()
                allowed = [c.strip().upper() for c in allowed_cargos]
                if cargo_user not in allowed:
                    return JsonResponse(
                        {"success": False, "error": "No tienes permisos para esta acción"},
                        status=403
                    )

       
            if enforce_mesa:
                cargo_user = (usuario.cargo or "").strip().upper()
                # cargos con acceso global (ajusta si quieres)
                cargos_globales = {"ADMIN", "SUPERVISOR"}

                if cargo_user not in cargos_globales:
                    mesa_req = (
                        request.GET.get("mesa")
                        or request.GET.get("numero_mesa")
                        or None
                    )
                    if request.method in ("POST", "PUT", "PATCH"):
                        # intenta leer mesa desde body JSON si viene
                        try:
                            import json
                            body = json.loads(request.body.decode("utf-8") or "{}")
                            mesa_req = mesa_req or body.get("mesa") or body.get("numero_mesa")
                        except Exception:
                            pass

                    if mesa_req is not None:
                        mesa_req = str(mesa_req).strip()
                        mesa_user = str(usuario.mesa).strip()
                        if mesa_req and mesa_user and mesa_req != mesa_user:
                            return JsonResponse(
                                {"success": False, "error": "No puedes operar sobre otra mesa"},
                                status=403
                            )

            return func(request, *args, **kwargs)

        return wrapper

    # Permite usarlo como @jwt_required o como @jwt_required(...)
    if view_func:
        return decorator(view_func)
    return decorator
