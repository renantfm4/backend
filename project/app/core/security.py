import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Gera o hash e decodifica para string (UTF-8)
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')



from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..core.config import SECRET_KEY, ALGORITHM
import uuid
import secrets

def generate_invite_token(email: str):
    expire = datetime.now() + timedelta(days=1)  # Token válido por 1 dia
    token_id = secrets.token_urlsafe(32)
    payload = {"sub": email, "exp": expire, "jti": token_id, "iat": datetime.timestamp(datetime.now())}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_invite_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
async def verify_user_invite_token(token: str, db_token: str, token_used: bool = False) -> bool:
    if token_used:
        return False
    if not db_token:
        return False
    if token != db_token:
        return False
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return False


def generate_reset_token(email: str):
    expire = datetime.now() + timedelta(hours=1)  # Token válido por 1 hora
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]  # Retorna o email do usuário
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
