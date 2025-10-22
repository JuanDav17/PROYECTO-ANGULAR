from fastapi import APIRouter, HTTPException, Header
from database import get_connection
from schemas.producto_schemas import ProductoCreate, ProductoResponse, ProductoUpdate
from auth import get_current_user, is_admin, is_vendedor, can_manage_producto
from typing import Optional

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=list[ProductoResponse])
def get_productos(activos_solo: bool = True):
    """Obtener todos los productos (públicos para todos)"""
    conn = get_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error al conectar a la base de datos")
    
    cursor = conn.cursor(dictionary=True)
    try:
        if activos_solo:
            query = """
                SELECT p.*, u.nombre as vendedor_nombre 
                FROM productos p
                JOIN usuarios u ON p.vendedor_id = u.id
                WHERE p.activo = TRUE AND u.activo = TRUE
                ORDER BY p.created_at DESC
            """
        else:
            query = """
                SELECT p.*, u.nombre as vendedor_nombre 
                FROM productos p
                JOIN usuarios u ON p.vendedor_id = u.id
                ORDER BY p.created_at DESC
            """
        
        cursor.execute(query)
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/mis-productos", response_model=list[ProductoResponse])
def get_mis_productos(authorization: Optional[str] = Header(None)):
    """Obtener productos del vendedor autenticado"""
    user = get_current_user(authorization)
    
    if not is_vendedor(user) and not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo vendedores pueden ver sus productos")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.*, u.nombre as vendedor_nombre 
            FROM productos p
            JOIN usuarios u ON p.vendedor_id = u.id
            WHERE p.vendedor_id = %s
            ORDER BY p.created_at DESC
        """
        cursor.execute(query, (user["id"],))
        productos = cursor.fetchall()
        return productos
    finally:
        cursor.close()
        conn.close()

@router.get("/{id}", response_model=ProductoResponse)
def get_producto(id: int):
    """Obtener producto por ID (público)"""
    conn = get_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error al conectar a la base de datos")
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.*, u.nombre as vendedor_nombre 
            FROM productos p
            JOIN usuarios u ON p.vendedor_id = u.id
            WHERE p.id = %s
        """
        cursor.execute(query, (id,))
        producto = cursor.fetchone()
        
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        return producto
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, authorization: Optional[str] = Header(None)):
    """Crear producto (solo vendedores y admin)"""
    user = get_current_user(authorization)
    
    if not is_vendedor(user) and not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo vendedores pueden crear productos")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """INSERT INTO productos (nombre, descripcion, precio, cantidad, vendedor_id) 
               VALUES (%s, %s, %s, %s, %s)""",
            (producto.nombre, producto.descripcion, producto.precio, producto.cantidad, user["id"])
        )
        conn.commit()
        producto_id = cursor.lastrowid
        
        cursor.execute("""
            SELECT p.*, u.nombre as vendedor_nombre 
            FROM productos p
            JOIN usuarios u ON p.vendedor_id = u.id
            WHERE p.id = %s
        """, (producto_id,))
        nuevo = cursor.fetchone()
        
        return nuevo
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{id}", response_model=ProductoResponse)
def actualizar_producto(
    id: int, 
    producto: ProductoUpdate, 
    authorization: Optional[str] = Header(None)
):
    """Actualizar producto (solo el vendedor dueño o admin)"""
    user = get_current_user(authorization)
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar que el producto existe y obtener el vendedor
        cursor.execute("SELECT vendedor_id FROM productos WHERE id = %s", (id,))
        prod = cursor.fetchone()
        
        if not prod:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Verificar permisos
        if not can_manage_producto(user, prod["vendedor_id"]):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para editar este producto"
            )
        
        # Construir query dinámica
        fields = []
        params = []
        
        if producto.nombre is not None:
            fields.append("nombre = %s")
            params.append(producto.nombre)
        if producto.descripcion is not None:
            fields.append("descripcion = %s")
            params.append(producto.descripcion)
        if producto.precio is not None:
            fields.append("precio = %s")
            params.append(producto.precio)
        if producto.cantidad is not None:
            fields.append("cantidad = %s")
            params.append(producto.cantidad)
        
        if not fields:
            raise HTTPException(
                status_code=400, 
                detail="No se proporcionaron campos para actualizar"
            )
        
        params.append(id)
        query = f"UPDATE productos SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        conn.commit()
        
        cursor.execute("""
            SELECT p.*, u.nombre as vendedor_nombre 
            FROM productos p
            JOIN usuarios u ON p.vendedor_id = u.id
            WHERE p.id = %s
        """, (id,))
        actualizado = cursor.fetchone()
        
        return actualizado
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar producto: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{id}")
def eliminar_producto(id: int, authorization: Optional[str] = Header(None)):
    """Eliminar/desactivar producto (solo el vendedor dueño o admin)"""
    user = get_current_user(authorization)
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar que el producto existe
        cursor.execute("SELECT vendedor_id FROM productos WHERE id = %s", (id,))
        prod = cursor.fetchone()
        
        if not prod:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Verificar permisos
        if not can_manage_producto(user, prod["vendedor_id"]):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para eliminar este producto"
            )
        
        # Desactivar en lugar de eliminar
        cursor.execute("UPDATE productos SET activo = FALSE WHERE id = %s", (id,))
        conn.commit()
        
        return {"message": "Producto desactivado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {str(e)}")
    finally:
        cursor.close()
        conn.close()