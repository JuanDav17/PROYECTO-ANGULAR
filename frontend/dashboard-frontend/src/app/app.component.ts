// src/app/app.component.ts
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  constructor(private router: Router) { }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('usuario'); 
  }

  logout(): void {
    localStorage.removeItem('usuario'); 
    this.router.navigate(['/login']); 
  }
}