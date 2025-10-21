from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status
from database import get_connection
from schemas.producto_schemas import ProductoCreate, ProductoResponse, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["Productos"])

# 📌 Obtener todos los productos
@router.get("/", response_model=list[ProductoResponse])
def get_productos():
    conn = get_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "Error al conectar a la base de datos"})
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al obtener productos: {e}"})
    finally:
        cursor.close()
        conn.close()


# 📌 Obtener producto por ID
@router.get("/{id}", response_model=ProductoResponse)
def get_producto(id: int):
    conn = get_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "Error al conectar a la base de datos"})
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        producto = cursor.fetchone()
        if not producto:
            return JSONResponse(status_code=404, content={"error": "Producto no encontrado"})
        return producto
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al obtener producto: {e}"})
    finally:
        cursor.close()
        conn.close()


# 📌 Crear producto
@router.post("/", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate):
    conn = get_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "Error al conectar a la base de datos"})

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO productos (nombre, descripcion, precio, cantidad) VALUES (%s, %s, %s, %s)",
            (producto.nombre, producto.descripcion, producto.precio, producto.cantidad)
        )
        conn.commit()
        producto_id = cursor.lastrowid
        cursor.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
        nuevo = cursor.fetchone()
        return nuevo
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al crear producto: {e}"})
    finally:
        cursor.close()
        conn.close()


# 📌 Actualizar producto
@router.put("/{id}", response_model=ProductoResponse)
def actualizar_producto(id: int, producto: ProductoUpdate):
    conn = get_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "Error al conectar a la base de datos"})

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        existente = cursor.fetchone()
        if not existente:
            return JSONResponse(status_code=404, content={"error": "Producto no encontrado"})

        cursor.execute(
            "UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s WHERE id = %s",
            (producto.nombre, producto.descripcion, producto.precio, producto.cantidad, id)
        )
        conn.commit()
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        actualizado = cursor.fetchone()
        return actualizado
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al actualizar producto: {e}"})
    finally:
        cursor.close()
        conn.close()


# 📌 Eliminar producto
@router.delete("/{id}")
def eliminar_producto(id: int):
    conn = get_connection()
    if conn is None:
        return JSONResponse(status_code=500, content={"error": "Error al conectar a la base de datos"})

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        existente = cursor.fetchone()
        if not existente:
            return JSONResponse(status_code=404, content={"error": "Producto no encontrado"})

        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conn.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Producto eliminado correctamente"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al eliminar producto: {e}"})
    finally:
        cursor.close()
        conn.close()