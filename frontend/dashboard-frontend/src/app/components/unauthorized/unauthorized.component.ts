import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-unauthorized',
  templateUrl: './unauthorized.component.html',
  styleUrls: ['./unauthorized.component.scss']
})
export class UnauthorizedComponent {
  
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  volverAtras(): void {
    this.router.navigate(['/']);
  }

  irADashboard(): void {
    const user = this.authService.currentUserValue;
    
    if (!user) {
      this.router.navigate(['/login']);
      return;
    }

    switch (user.rol) {
      case 'admin':
        this.router.navigate(['/admin/dashboard']);
        break;
      case 'vendedor':
        this.router.navigate(['/vendedor/dashboard']);
        break;
      case 'usuario':
        this.router.navigate(['/comprador/catalogo']);
        break;
      default:
        this.router.navigate(['/productos']);
    }
  }

  cerrarSesion(): void {
    this.authService.logout();
  }
}