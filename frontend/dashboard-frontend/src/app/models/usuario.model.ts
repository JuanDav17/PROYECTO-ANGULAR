export interface Usuario {
  id?: number;
  nombre: string;
  email: string;
  password?: string;
  rol: 'admin' | 'vendedor' | 'usuario';
  activo?: boolean;
  created_at?: Date;
}

export interface LoginResponse {
  token: string;
  usuario: Usuario;
}

export interface LoginRequest {
  email: string;
  password: string;
}