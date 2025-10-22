from fastapi import APIRouter, HTTPException, Header
from database import get_connection
from schemas.pedido_schemas import (
    PedidoCreate, 
    PedidoResponse, 
    DetallePedidoResponse, 
    PedidoUpdateEstado
)
from auth import get_current_user, is_admin
from typing import Optional

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=PedidoResponse)
def crear_pedido(pedido: PedidoCreate, authorization: Optional[str] = Header(None)):
    """Crear un nuevo pedido (compra) - Usuarios autenticados"""
    user = get_current_user(authorization)
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        conn.start_transaction()
        
        # Validar y calcular total
        total = 0
        items_validados = []
        
        for item in pedido.items:
            cursor.execute("""
                SELECT id, nombre, precio, cantidad, vendedor_id, activo 
                FROM productos 
                WHERE id = %s
            """, (item.producto_id,))
            
            producto = cursor.fetchone()
            
            if not producto:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Producto {item.producto_id} no encontrado"
                )
            
            if not producto["activo"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Producto {producto['nombre']} no está disponible"
                )
            
            if producto["cantidad"] < item.cantidad:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Stock insuficiente para {producto['nombre']}. Disponible: {producto['cantidad']}"
                )
            
            subtotal = producto["precio"] * item.cantidad
            total += subtotal
            
            items_validados.append({
                "producto_id": producto["id"],
                "nombre": producto["nombre"],
                "cantidad": item.cantidad,
                "precio_unitario": producto["precio"],
                "subtotal": subtotal,
                "vendedor_id": producto["vendedor_id"]
            })
        
        # Crear pedido
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, total) VALUES (%s, %s)",
            (user["id"], total)
        )
        pedido_id = cursor.lastrowid
        
        # Crear detalles del pedido y registrar ventas
        for item_val in items_validados:
            # Insertar detalle del pedido
            cursor.execute("""
                INSERT INTO detalle_pedidos 
                (pedido_id, producto_id, cantidad, precio_unitario, subtotal, vendedor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                pedido_id,
                item_val["producto_id"],
                item_val["cantidad"],
                item_val["precio_unitario"],
                item_val["subtotal"],
                item_val["vendedor_id"]
            ))
            detalle_id = cursor.lastrowid
            
            # Registrar venta para el vendedor
            cursor.execute("""
                INSERT INTO ventas 
                (vendedor_id, pedido_id, detalle_pedido_id, producto_id, cantidad, precio_unitario, total, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendiente')
            """, (
                item_val["vendedor_id"],
                pedido_id,
                detalle_id,
                item_val["producto_id"],
                item_val["cantidad"],
                item_val["precio_unitario"],
                item_val["subtotal"]
            ))
            
            # Actualizar stock del producto
            cursor.execute(
                "UPDATE productos SET cantidad = cantidad - %s WHERE id = %s",
                (item_val["cantidad"], item_val["producto_id"])
            )
        
        conn.commit()
        
        # Obtener el pedido completo con sus detalles
        cursor.execute("""
            SELECT p.*, u.nombre as usuario_nombre
            FROM pedidos p
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.id = %s
        """, (pedido_id,))
        pedido_data = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                dp.id,
                dp.producto_id,
                prod.nombre as producto_nombre,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal,
                dp.vendedor_id
            FROM detalle_pedidos dp
            JOIN productos prod ON dp.producto_id = prod.id
            WHERE dp.pedido_id = %s
        """, (pedido_id,))
        items_response = cursor.fetchall()
        
        return {
            "id": pedido_data["id"],
            "usuario_id": pedido_data["usuario_id"],
            "total": pedido_data["total"],
            "estado": pedido_data["estado"],
            "created_at": pedido_data["created_at"],
            "items": items_response
        }
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear pedido: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/mis-pedidos", response_model=list[PedidoResponse])
def get_mis_pedidos(authorization: Optional[str] = Header(None)):
    """Obtener pedidos del usuario autenticado"""
    user = get_current_user(authorization)
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM pedidos 
            WHERE usuario_id = %s 
            ORDER BY created_at DESC
        """, (user["id"],))
        pedidos = cursor.fetchall()
        
        # Obtener detalles de cada pedido
        result = []
        for pedido in pedidos:
            cursor.execute("""
                SELECT 
                    dp.id,
                    dp.producto_id,
                    prod.nombre as producto_nombre,
                    dp.cantidad,
                    dp.precio_unitario,
                    dp.subtotal,
                    dp.vendedor_id
                FROM detalle_pedidos dp
                JOIN productos prod ON dp.producto_id = prod.id
                WHERE dp.pedido_id = %s
            """, (pedido["id"],))
            items = cursor.fetchall()
            
            result.append({
                "id": pedido["id"],
                "usuario_id": pedido["usuario_id"],
                "total": pedido["total"],
                "estado": pedido["estado"],
                "created_at": pedido["created_at"],
                "items": items
            })
        
        return result
    finally:
        cursor.close()
        conn.close()

@router.get("/", response_model=list[PedidoResponse])
def listar_todos_pedidos(authorization: Optional[str] = Header(None)):
    """Listar todos los pedidos (solo admin)"""
    user = get_current_user(authorization)
    
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM pedidos ORDER BY created_at DESC")
        pedidos = cursor.fetchall()
        
        result = []
        for pedido in pedidos:
            cursor.execute("""
                SELECT 
                    dp.id,
                    dp.producto_id,
                    prod.nombre as producto_nombre,
                    dp.cantidad,
                    dp.precio_unitario,
                    dp.subtotal,
                    dp.vendedor_id
                FROM detalle_pedidos dp
                JOIN productos prod ON dp.producto_id = prod.id
                WHERE dp.pedido_id = %s
            """, (pedido["id"],))
            items = cursor.fetchall()
            
            result.append({
                "id": pedido["id"],
                "usuario_id": pedido["usuario_id"],
                "total": pedido["total"],
                "estado": pedido["estado"],
                "created_at": pedido["created_at"],
                "items": items
            })
        
        return result
    finally:
        cursor.close()
        conn.close()

@router.get("/{pedido_id}", response_model=PedidoResponse)
def get_pedido(pedido_id: int, authorization: Optional[str] = Header(None)):
    """Obtener detalle de un pedido"""
    user = get_current_user(authorization)
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verificar permisos: solo el dueño o admin pueden ver el pedido
        if pedido["usuario_id"] != user["id"] and not is_admin(user):
            raise HTTPException(status_code=403, detail="No tienes permisos para ver este pedido")
        
        cursor.execute("""
            SELECT 
                dp.id,
                dp.producto_id,
                prod.nombre as producto_nombre,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal,
                dp.vendedor_id
            FROM detalle_pedidos dp
            JOIN productos prod ON dp.producto_id = prod.id
            WHERE dp.pedido_id = %s
        """, (pedido_id,))
        items = cursor.fetchall()
        
        return {
            "id": pedido["id"],
            "usuario_id": pedido["usuario_id"],
            "total": pedido["total"],
            "estado": pedido["estado"],
            "created_at": pedido["created_at"],
            "items": items
        }
    finally:
        cursor.close()
        conn.close()

@router.put("/{pedido_id}/estado")
def actualizar_estado_pedido(
    pedido_id: int, 
    datos: PedidoUpdateEstado, 
    authorization: Optional[str] = Header(None)
):
    """Actualizar estado de un pedido (solo admin)"""
    user = get_current_user(authorization)
    
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo administradores pueden cambiar el estado")
    
    estados_validos = ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']
    if datos.estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Valores permitidos: {', '.join(estados_validos)}")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (datos.estado, pedido_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Actualizar estado en la tabla ventas
        cursor.execute("UPDATE ventas SET estado = %s WHERE pedido_id = %s", (datos.estado, pedido_id))
        conn.commit()
        
        return {"message": "Estado del pedido actualizado correctamente"}
    finally:
        cursor.close()
        conn.close()