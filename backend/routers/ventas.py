from fastapi import APIRouter, HTTPException, Header
from database import get_connection
from schemas.venta_schemas import VentaResponse, EstadisticasVendedor
from auth import get_current_user, is_vendedor, is_admin
from typing import Optional

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.get("/mis-ventas", response_model=list[VentaResponse])
def get_mis_ventas(authorization: Optional[str] = Header(None)):
    """Obtener ventas del vendedor autenticado"""
    user = get_current_user(authorization)
    
    if not is_vendedor(user) and not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo vendedores pueden ver sus ventas")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                v.id,
                v.pedido_id,
                v.producto_id,
                p.nombre as producto_nombre,
                v.cantidad,
                v.precio_unitario,
                v.total,
                v.estado,
                u.nombre as cliente_nombre,
                v.created_at
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            JOIN pedidos ped ON v.pedido_id = ped.id
            JOIN usuarios u ON ped.usuario_id = u.id
            WHERE v.vendedor_id = %s
            ORDER BY v.created_at DESC
        """
        cursor.execute(query, (user["id"],))
        ventas = cursor.fetchall()
        return ventas
    finally:
        cursor.close()
        conn.close()

@router.get("/estadisticas", response_model=EstadisticasVendedor)
def get_estadisticas_vendedor(authorization: Optional[str] = Header(None)):
    """Obtener estadísticas del vendedor"""
    user = get_current_user(authorization)
    
    if not is_vendedor(user) and not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo vendedores pueden ver estadísticas")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Total de ventas
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0) as total_ventas
            FROM ventas
            WHERE vendedor_id = %s
        """, (user["id"],))
        total_ventas = cursor.fetchone()["total_ventas"]
        
        # Total productos vendidos
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) as total_productos
            FROM ventas
            WHERE vendedor_id = %s
        """, (user["id"],))
        total_productos_vendidos = cursor.fetchone()["total_productos"]
        
        # Productos publicados
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM productos
            WHERE vendedor_id = %s AND activo = TRUE
        """, (user["id"],))
        productos_publicados = cursor.fetchone()["total"]
        
        # Ventas pendientes
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM ventas
            WHERE vendedor_id = %s AND estado = 'pendiente'
        """, (user["id"],))
        ventas_pendientes = cursor.fetchone()["total"]
        
        # Ventas completadas
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM ventas
            WHERE vendedor_id = %s AND estado = 'entregado'
        """, (user["id"],))
        ventas_completadas = cursor.fetchone()["total"]
        
        return {
            "total_ventas": float(total_ventas),
            "total_productos_vendidos": int(total_productos_vendidos),
            "productos_publicados": int(productos_publicados),
            "ventas_pendientes": int(ventas_pendientes),
            "ventas_completadas": int(ventas_completadas)
        }
    finally:
        cursor.close()
        conn.close()

@router.get("/", response_model=list[VentaResponse])
def listar_todas_ventas(authorization: Optional[str] = Header(None)):
    """Listar todas las ventas (solo admin)"""
    user = get_current_user(authorization)
    
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver todas las ventas")
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                v.id,
                v.pedido_id,
                v.producto_id,
                p.nombre as producto_nombre,
                v.cantidad,
                v.precio_unitario,
                v.total,
                v.estado,
                u.nombre as cliente_nombre,
                v.created_at
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            JOIN pedidos ped ON v.pedido_id = ped.id
            JOIN usuarios u ON ped.usuario_id = u.id
            ORDER BY v.created_at DESC
        """
        cursor.execute(query)
        ventas = cursor.fetchall()
        return ventas
    finally:
        cursor.close()
        conn.close()