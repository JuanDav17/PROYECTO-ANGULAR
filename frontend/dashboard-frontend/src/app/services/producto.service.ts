import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Producto } from '../models/producto.model';

@Injectable({
  providedIn: 'root'
})
export class ProductoService {

  private apiUrl = 'http://localhost:3000/productos'; // URL del backend FastAPI

  constructor(private http: HttpClient) {}

  obtenerProductos(): Observable<Producto[]> {
    return this.http.get<Producto[]>(this.apiUrl);
  }

  agregarProducto(producto: Producto): Observable<any> {
    return this.http.post(this.apiUrl, producto);
  }

  actualizarProducto(id: number, producto: Producto): Observable<any> {
    return this.http.put(${this.apiUrl}/${id}, producto);
  }

  eliminarProducto(id: number): Observable<any> {
    return this.http.delete(${this.apiUrl}/${id});
  }
}