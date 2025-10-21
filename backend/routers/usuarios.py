from fastapi import APIRouter
from fastapi.responses import JSONResponse
from database import get_connection
from schemas.usuario_schemas import UsuarioCreate, UsuarioResponse, LoginRequest
import bcrypt

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Registrar usuario
@router.post("/registro", response_model=UsuarioResponse)
def registrar_usuario(usuario: UsuarioCreate):
    conn = get_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "Error al conectar a la base de datos"})

    cursor = conn.cursor(dictionary=True)
    try:
        # Encriptar contraseña
        hashed_pw = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (usuario.nombre, usuario.email, hashed_pw.decode('utf-8'))
        )
        conn.commit()
        user_id = cursor.lastrowid

        cursor.execute("SELECT id, nombre, email, rol FROM usuarios WHERE id = %s", (user_id,))
        nuevo_usuario = cursor.fetchone()

        return nuevo_usuario
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al registrar usuario: {e}"})
    finally:
        cursor.close()
        conn.close()


# Login de usuario
@router.post("/login")
def login(usuario: LoginRequest):
    conn = get_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "Error al conectar a la base de datos"})

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (usuario.email,))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(usuario.password.encode('utf-8'), user["password"].encode('utf-8')):
            return JSONResponse(status_code=401, content={"error": "Credenciales incorrectas"})

        return {"message": "Login exitoso", "usuario": {"id": user["id"], "nombre": user["nombre"], "rol": user["rol"]}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error en login: {e}"})
    finally:
        cursor.close()
        conn.close()




