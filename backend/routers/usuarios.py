from fastapi import APIRouter, HTTPException, Header
from database import get_connection
from schemas.usuario_schemas import (
    UsuarioCreate, 
    UsuarioResponse, 
    LoginRequest, 
    LoginResponse
)
from auth import create_access_token, get_current_user, is_admin
import bcrypt
from typing import Optional

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/registro", response_model=UsuarioResponse)
def registrar_usuario(usuario: UsuarioCreate):
    """Registro de nuevo usuario"""
    conn = get_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error al conectar a la base de datos")

    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar si el email ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (usuario.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        # Validar rol
        if usuario.rol not in ['usuario', 'vendedor', 'admin']:
            usuario.rol = 'usuario'

        # Encriptar contraseña
        hashed_pw = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)",
            (usuario.nombre, usuario.email, hashed_pw.decode('utf-8'), usuario.rol)
        )
        conn.commit()
        user_id = cursor.lastrowid

        cursor.execute(
            "SELECT id, nombre, email, rol, activo, created_at FROM usuarios WHERE id = %s", 
            (user_id,)
        )
        nuevo_usuario = cursor.fetchone()

        return nuevo_usuario
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/login", response_model=LoginResponse)
def login(usuario: LoginRequest):
    """Login de usuario con token JWT"""
    conn = get_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error al conectar a la base de datos")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (usuario.email,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
        if not user.get("activo"):
            raise HTTPException(status_code=401, detail="Usuario inactivo")

        if not bcrypt.checkpw(usuario.password.encode('utf-8'), user["password"].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Crear token
        token = create_access_token({
            "user_id": user["id"],
            "email": user["email"],
            "rol": user["rol"]
        })

        # Preparar respuesta sin password
        user_data = {
            "id": user["id"],
            "nombre": user["nombre"],
            "email": user["email"],
            "rol": user["rol"],
            "activo": user["activo"],
            "created_at": user["created_at"]
        }

        return {"token": token, "usuario": user_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/me", response_model=UsuarioResponse)
def get_mi_perfil(authorization: Optional[str] = Header(None)):
    """Obtener perfil del usuario autenticado"""
    user = get_current_user(authorization)
    return user

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(authorization: Optional[str] = Header(None)):
    """Listar todos los usuarios (solo admin)"""
    user = get_current_user(authorization)
    
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, nombre, email, rol, activo, created_at FROM usuarios ORDER BY created_at DESC"
        )
        usuarios = cursor.fetchall()
        return usuarios
    finally:
        cursor.close()
        conn.close()

@router.put("/{usuario_id}/rol")
def cambiar_rol(
    usuario_id: int, 
    nuevo_rol: str, 
    authorization: Optional[str] = Header(None)
):
    """Cambiar rol de usuario (solo admin)"""
    user = get_current_user(authorization)
    
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores")
    
    if nuevo_rol not in ['usuario', 'vendedor', 'admin']:
        raise HTTPException(status_code=400, detail="Rol inválido")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET rol = %s WHERE id = %s", (nuevo_rol, usuario_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {"message": "Rol actualizado correctamente"}
    finally:
        cursor.close()
        conn.close()

@router.put("/{usuario_id}/estado")
def cambiar_estado(
    usuario_id: int, 
    activo: bool, 
    authorization: Optional[str] = Header(None)
):
    """Activar/desactivar usuario (solo admin)"""
    user = get_current_user(authorization)
    
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET activo = %s WHERE id = %s", (activo, usuario_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {"message": f"Usuario {'activado' if activo else 'desactivado'} correctamente"}
    finally:
        cursor.close()
        conn.close()