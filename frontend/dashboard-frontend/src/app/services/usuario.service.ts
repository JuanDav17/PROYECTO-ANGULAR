import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Usuario } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {

  private apiUrl = 'http://localhost:3000/usuarios'; // URL del backend FastAPI

  constructor(private http: HttpClient) {}

  registrar(usuario: Usuario): Observable<any> {
    return this.http.post(${this.apiUrl}/registro, usuario);
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(${this.apiUrl}/login, { email, password });
  }
}