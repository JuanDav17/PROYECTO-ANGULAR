export interface Venta {
  id: number;
  pedido_id: number;
  producto_id: number;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;
  total: number;
  estado: string;
  cliente_nombre: string;
  created_at: Date;
}

export interface EstadisticasVendedor {
  total_ventas: number;
  total_productos_vendidos: number;
  productos_publicados: number;
  ventas_pendientes: number;
  ventas_completadas: number;
}