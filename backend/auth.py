from fastapi import HTTPException, Header, status
from database import get_connection
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_cambiar_en_produccion_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

def create_access_token(data: dict):
    """Crear token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_current_user(authorization: Optional[str] = Header(None)):
    """Obtener usuario actual del token"""
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="No se proporcionó token de autenticación"
        )
    
    try:
        # Extraer token
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Obtener usuario de la base de datos
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, email, rol, activo FROM usuarios WHERE id = %s", 
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or not user.get("activo"):
            raise HTTPException(
                status_code=401, 
                detail="Usuario no encontrado o inactivo"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Error de autenticación: {str(e)}"
        )

def is_admin(user: dict) -> bool:
    """Verificar si el usuario es administrador"""
    return user.get("rol") == "admin"

def is_vendedor(user: dict) -> bool:
    """Verificar si el usuario es vendedor"""
    return user.get("rol") == "vendedor"

def is_usuario(user: dict) -> bool:
    """Verificar si el usuario es usuario normal"""
    return user.get("rol") == "usuario"

def can_manage_producto(user: dict, producto_vendedor_id: int) -> bool:
    """Verificar si el usuario puede gestionar un producto"""
    return is_admin(user) or (is_vendedor(user) and user["id"] == producto_vendedor_id)