import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { ProductosComponent } from './components/productos/productos.component';
import { UnauthorizedComponent } from './components/unauthorized/unauthorized.component';

const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'unauthorized', component: UnauthorizedComponent },

  // Rutas protegidas
  {
    path: 'productos',
    component: ProductosComponent,
    canActivate: [AuthGuard]
  },

  // Rutas para VENDEDORES
  {
    path: 'vendedor',
    canActivate: [AuthGuard],
    data: { roles: ['vendedor', 'admin'] },
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      // Componentes pendientes
    ]
  },

  // Rutas para ADMIN
  {
    path: 'admin',
    canActivate: [AuthGuard],
    data: { roles: ['admin'] },
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      // Componentes pendientes
    ]
  },

  // Rutas para USUARIO
  {
    path: 'comprador',
    canActivate: [AuthGuard],
    data: { roles: ['usuario', 'admin'] },
    children: [
      { path: '', redirectTo: 'catalogo', pathMatch: 'full' },
      // Componentes pendientes
    ]
  },

  { path: '**', redirectTo: 'login' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }