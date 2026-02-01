from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def web_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get("web_user_id"):
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect("iniciose")  
        return view_func(request, *args, **kwargs)
    return _wrapped
