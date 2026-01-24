import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings

from django.utils import timezone
def _crear_token(payload: dict, exp_delta: timedelta):
    """
    Crea un JWT firmado con SECRET_KEY, agregando iat/exp/jti.
    """
    ahora = timezone.now()

    data = dict(payload or {})
    data["iat"] = int(ahora.timestamp())
    data["exp"] = int((ahora + exp_delta).timestamp())
    data["jti"] = str(uuid.uuid4())

    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")


def crear_access_token(payload: dict, minutes: int = 60):
    """
    Crea access token que expira en X minutos.
    Se usa así: crear_access_token(payload, minutes=60)
    """
    return _crear_token(payload, timedelta(minutes=int(minutes)))


def crear_refresh_token(payload: dict, days: int = 7):
    """
    Crea refresh token que expira en X días.
    Se usa así: crear_refresh_token(payload, days=7)
    """
    return _crear_token(payload, timedelta(days=int(days)))


def decodificar_token(token: str):
    """
    Decodifica JWT y valida firma + expiración.
    Leeway=60 permite tolerancia de reloj (evita iat "del futuro" por segundos).
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=["HS256"],
        leeway=60
    )
