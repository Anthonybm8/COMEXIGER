from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from Aplicaciones.Usuario.models import Usuario


def _get_session_user(request):
    user_id = request.session.get("web_user_id")
    if not user_id:
        return None

    try:
        return Usuario.objects.get(id=int(user_id))
    except (ValueError, TypeError, Usuario.DoesNotExist):
        request.session.flush()
        return None


def web_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        usuario = _get_session_user(request)
        if not usuario:
            messages.warning(request, "Debes iniciar sesion para acceder.")
            return redirect("iniciose")

        request.web_user = usuario
        return view_func(request, *args, **kwargs)

    return _wrapped


def web_admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        usuario = _get_session_user(request)
        if not usuario:
            messages.warning(request, "Debes iniciar sesion para acceder.")
            return redirect("iniciose")

        if (usuario.cargo or "").strip().upper() != "ADMIN":
            messages.error(request, "ACCESO DENEGADO.")
            return redirect("iniciose")

        request.web_user = usuario
        return view_func(request, *args, **kwargs)

    return _wrapped
