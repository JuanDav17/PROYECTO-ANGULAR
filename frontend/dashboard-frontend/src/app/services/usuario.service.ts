import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Usuario } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private apiUrl = 'http://localhost:3000/usuarios';

  constructor(private http: HttpClient) {}

  listarUsuarios(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(this.apiUrl);
  }

  cambiarRol(usuarioId: number, nuevoRol: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${usuarioId}/rol`, null, {
      params: { nuevo_rol: nuevoRol }
    });
  }

  cambiarEstado(usuarioId: number, activo: boolean): Observable<any> {
    return this.http.put(`${this.apiUrl}/${usuarioId}/estado`, null, {
      params: { activo: activo.toString() }
    });
  }
}