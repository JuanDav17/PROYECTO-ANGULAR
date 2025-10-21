import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  nombre = '';
  email = '';
  password = '';

  private apiUrl = 'http://localhost:3000/usuarios/registro'; // URL del backend

  constructor(private http: HttpClient, private router: Router) {}

  onSubmit() {
    const userData = {
      nombre: this.nombre,
      email: this.email,
      password: this.password
    };

    this.http.post(this.apiUrl, userData).subscribe({
      next: (response) => {
        alert('Usuario registrado exitosamente');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        alert('Error al registrar usuario');
        console.error(err);
      }
    });
  }
}