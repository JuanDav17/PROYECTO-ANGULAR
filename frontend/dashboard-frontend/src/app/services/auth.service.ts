import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Usuario, LoginResponse, LoginRequest } from '../models/usuario.model';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:3000/usuarios';
  private currentUserSubject: BehaviorSubject<Usuario | null>;
  public currentUser: Observable<Usuario | null>;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    const storedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<Usuario | null>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): Usuario | null {
    return this.currentUserSubject.value;
  }

  public get token(): string | null {
    return localStorage.getItem('token');
  }

  public get isAuthenticated(): boolean {
    return !!this.token;
  }

  public get isAdmin(): boolean {
    return this.currentUserValue?.rol === 'admin';
  }

  public get isVendedor(): boolean {
    return this.currentUserValue?.rol === 'vendedor';
  }

  public get isUsuario(): boolean {
    return this.currentUserValue?.rol === 'usuario';
  }

  registro(usuario: Usuario): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/registro`, usuario);
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credentials)
      .pipe(
        tap(response => {
          // Guardar token y usuario
          localStorage.setItem('token', response.token);
          localStorage.setItem('currentUser', JSON.stringify(response.usuario));
          this.currentUserSubject.next(response.usuario);
        })
      );
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  getMiPerfil(): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/me`);
  }

  // Métodos para admin
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