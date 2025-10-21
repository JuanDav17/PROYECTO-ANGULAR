# crud.py
from database import get_connection
from passlib.context import CryptContext
from mysql.connector import Error

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Usuarios ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_usuario(nombre: str, email: str, password: str, rol: str = "usuario"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        hashed = hash_password(password)
        sql = "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (nombre, email, hashed, rol))
        conn.commit()
        lastid = cur.lastrowid
        cur.close()
        return lastid
    except Error as e:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_usuario_by_id(usuario_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, nombre, email, rol, created_at FROM usuarios WHERE id = %s", (usuario_id,))
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        conn.close()

def get_usuarios(limit: int = 100, offset: int = 0):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, nombre, email, rol, created_at FROM usuarios LIMIT %s OFFSET %s", (limit, offset))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

def update_usuario(usuario_id: int, nombre=None, email=None, password=None, rol=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        fields = []
        params = []
        if nombre is not None:
            fields.append("nombre = %s"); params.append(nombre)
        if email is not None:
            fields.append("email = %s"); params.append(email)
        if password is not None:
            fields.append("password = %s"); params.append(hash_password(password))
        if rol is not None:
            fields.append("rol = %s"); params.append(rol)
        if not fields:
            return False
        sql = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"
        params.append(usuario_id)
        cur.execute(sql, tuple(params))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0
    finally:
        conn.close()

def delete_usuario(usuario_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0
    finally:
        conn.close()


# --- Productos ---
def create_producto(nombre: str, descripcion: str, precio: float, cantidad: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        sql = "INSERT INTO productos (nombre, descripcion, precio, cantidad) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (nombre, descripcion, precio, cantidad))
        conn.commit()
        lastid = cur.lastrowid
        cur.close()
        return lastid
    finally:
        conn.close()

def get_producto_by_id(producto_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        conn.close()

def get_productos(limit: int = 100, offset: int = 0):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM productos LIMIT %s OFFSET %s", (limit, offset))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

def update_producto(producto_id: int, nombre=None, descripcion=None, precio=None, cantidad=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        fields = []
        params = []
        if nombre is not None:
            fields.append("nombre = %s"); params.append(nombre)
        if descripcion is not None:
            fields.append("descripcion = %s"); params.append(descripcion)
        if precio is not None:
            fields.append("precio = %s"); params.append(precio)
        if cantidad is not None:
            fields.append("cantidad = %s"); params.append(cantidad)
        if not fields:
            return False
        sql = f"UPDATE productos SET {', '.join(fields)} WHERE id = %s"
        params.append(producto_id)
        cur.execute(sql, tuple(params))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0
    finally:
        conn.close()

def delete_producto(producto_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0
    finally:
        conn.close()