export interface DetallePedido {
  producto_id: number;
  cantidad: number;
}

export interface PedidoCreate {
  items: DetallePedido[];
}

export interface DetallePedidoResponse {
  id: number;
  producto_id: number;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
  vendedor_id: number;
}

export interface Pedido {
  id: number;
  usuario_id: number;
  total: number;
  estado: 'pendiente' | 'procesando' | 'enviado' | 'entregado' | 'cancelado';
  created_at: Date;
  items: DetallePedidoResponse[];
}