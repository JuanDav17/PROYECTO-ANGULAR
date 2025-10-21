// src/app/app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';          // <--- ¡IMPORTACIÓN CLAVE!
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router'; 

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { ProductosComponent } from './components/productos/productos.component';

@NgModule({
  declarations: [ 
    AppComponent,
    LoginComponent,
    RegisterComponent,
    ProductosComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,         // <--- CLAVE PARA NGMODEL
    HttpClientModule,    
    RouterModule,         
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }