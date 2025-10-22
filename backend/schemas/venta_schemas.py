from pydantic import BaseModel
from datetime import datetime

class VentaResponse(BaseModel):
    id: int
    pedido_id: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: float
    total: float
    estado: str
    cliente_nombre: str
    created_at: datetime

class EstadisticasVendedor(BaseModel):
    total_ventas: float
    total_productos_vendidos: int
    productos_publicados: int
    ventas_pendientes: int
    ventas_completadas: int