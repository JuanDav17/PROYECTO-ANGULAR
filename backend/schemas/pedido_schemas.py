from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DetallePedidoCreate(BaseModel):
    producto_id: int
    cantidad: int

class PedidoCreate(BaseModel):
    items: List[DetallePedidoCreate]

class DetallePedidoResponse(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    vendedor_id: int

class PedidoResponse(BaseModel):
    id: int
    usuario_id: int
    total: float
    estado: str
    created_at: datetime
    items: List[DetallePedidoResponse]

class PedidoUpdateEstado(BaseModel):
    estado: str