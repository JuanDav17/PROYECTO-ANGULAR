import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  email = '';
  password = '';

  private apiUrl = 'http://localhost:3000/usuarios/login'; // tu backend FastAPI

  constructor(private http: HttpClient, private router: Router) {}

  onLogin() {
    const loginData = {
      email: this.email,
      password: this.password
    };

    this.http.post<any>(this.apiUrl, loginData).subscribe({
      next: (response) => {
        alert('Inicio de sesión exitoso');
        localStorage.setItem('usuario', JSON.stringify(response.usuario));
        this.router.navigate(['/productos']); // redirige al CRUD después del login
      },
      error: (err) => {
        alert('Error al iniciar sesión: credenciales incorrectas');
        console.error(err);
      }
    });
  }
}