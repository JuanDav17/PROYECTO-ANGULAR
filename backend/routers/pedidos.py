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