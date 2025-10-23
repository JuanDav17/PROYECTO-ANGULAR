import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Venta, EstadisticasVendedor } from '../models/venta.model';

@Injectable({
  providedIn: 'root'
})
export class VentaService {
  private apiUrl = 'http://localhost:3000/ventas';

  constructor(private http: HttpClient) {}

  obtenerMisVentas(): Observable<Venta[]> {
    return this.http.get<Venta[]>(`${this.apiUrl}/mis-ventas`);
  }

  obtenerEstadisticas(): Observable<EstadisticasVendedor> {
    return this.http.get<EstadisticasVendedor>(`${this.apiUrl}/estadisticas`);
  }

  listarTodasVentas(): Observable<Venta[]> {
    return this.http.get<Venta[]>(this.apiUrl);
  }
}