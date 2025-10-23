import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  loading = false;
  submitted = false;
  error = '';

  constructor(
    private formBuilder: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    if (this.authService.isAuthenticated) {
      this.redirectByRole();
    }
  }

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  get f() {
    return this.loginForm.controls;
  }

  onSubmit(): void {
    this.submitted = true;
    this.error = '';

    console.log(' Formulario enviado');
    console.log(' Datos:', this.loginForm.value);

    if (this.loginForm.invalid) {
      console.log(' Formulario inválido');
      return;
    }

    this.loading = true;

    this.authService.login(this.loginForm.value).subscribe({
      next: (response) => {
        console.log(' Login exitoso:', response);
        this.redirectByRole();
      },
      error: (error) => {
        console.error(' Error en login:', error);
        console.error(' Error completo:', JSON.stringify(error, null, 2));
        
        this.error = error.error?.detail || 
                     error.message || 
                     'Error al iniciar sesión. Verifica tus credenciales.';
        this.loading = false;
      },
      complete: () => {
        console.log(' Login completado');
        this.loading = false;
      }
    });
  }

  redirectByRole(): void {
    const user = this.authService.currentUserValue;
    console.log('👤 Usuario actual:', user);
    
    if (!user) {
      console.log(' No hay usuario');
      return;
    }

    switch (user.rol) {
      case 'admin':
        console.log(' Redirigiendo a admin');
        this.router.navigate(['/productos']);
        break;
      case 'vendedor':
        console.log(' Redirigiendo a vendedor');
        this.router.navigate(['/productos']);
        break;
      case 'usuario':
        console.log(' Redirigiendo a comprador');
        this.router.navigate(['/productos']);
        break;
      default:
        console.log(' Redirigiendo por defecto');
        this.router.navigate(['/productos']);
    }
  }

  irARegistro(): void {
    this.router.navigate(['/register']);
  }
}