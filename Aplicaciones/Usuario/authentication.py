from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Usuario
from .jwt_utils import decodificar_token

class UsuarioJWTAuthentication(BaseAuthentication):
    """
    Lee: Authorization: Bearer <token>
    Decodifica JWT firmado con SECRET_KEY y devuelve un Usuario (tu modelo).
    """

    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth:
            return None  # sin credenciales

        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Formato Authorization inválido. Usa: Bearer <token>")

        token = parts[1].strip()
        try:
            payload = decodificar_token(token)
        except Exception:
            raise AuthenticationFailed("Token inválido o expirado")

        if payload.get("type") != "access":
            raise AuthenticationFailed("Token incorrecto (se requiere access token)")

        usuario_id = payload.get("sub")
        if not usuario_id:
            raise AuthenticationFailed("Token sin 'sub'")

        try:
            usuario = Usuario.objects.get(id=int(usuario_id))
        except Usuario.DoesNotExist:
            raise AuthenticationFailed("Usuario no existe")

        # DRF espera (user, auth). auth puede ser None
        return (usuario, None)
