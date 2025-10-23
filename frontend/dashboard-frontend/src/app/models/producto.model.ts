export interface Producto {
  id?: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  cantidad: number;
  vendedor_id?: number;
  vendedor_nombre?: string;
  activo?: boolean;
  created_at?: Date;
}