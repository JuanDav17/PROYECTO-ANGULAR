export interface Usuario {
  id?: number;
  nombre: string;
  email: string;
  password: string;
  rol?: 'admin' | 'usuario';
  created_at?: string;
}