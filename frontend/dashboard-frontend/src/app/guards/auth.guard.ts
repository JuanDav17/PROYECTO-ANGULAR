import { Injectable } from '@angular/core';
import { 
  ActivatedRouteSnapshot, 
  CanActivate, 
  Router, 
  RouterStateSnapshot, 
  UrlTree 
} from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    if (this.authService.isAuthenticated) {
      // Verificar roles si están especificados en la ruta
      const roles = route.data['roles'] as string[];
      
      if (roles && roles.length > 0) {
        const userRole = this.authService.currentUserValue?.rol;
        
        if (userRole && roles.includes(userRole)) {
          return true;
        } else {
          // No tiene el rol necesario
          this.router.navigate(['/unauthorized']);
          return false;
        }
      }
      
      return true;
    }

    // No está autenticado
    this.router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
    return false;
  }
}