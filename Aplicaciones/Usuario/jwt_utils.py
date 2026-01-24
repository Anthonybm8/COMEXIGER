import jwt
from datetime import datetime, timedelta
from django.conf import settings

ALGORITHM = "HS256"

def crear_access_token(payload: dict, minutes: int = 60):
    now = datetime.utcnow()
    data = {
        **payload,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)

def crear_refresh_token(payload: dict, days: int = 7):
    now = datetime.utcnow()
    data = {
        **payload,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=days),
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
