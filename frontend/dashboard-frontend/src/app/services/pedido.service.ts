import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Pedido, PedidoCreate } from '../models/pedido.model';

@Injectable({
  providedIn: 'root'
})
export class PedidoService {
  private apiUrl = 'http://localhost:3000/pedidos';

  constructor(private http: HttpClient) {}

  crearPedido(pedido: PedidoCreate): Observable<Pedido> {
    return this.http.post<Pedido>(this.apiUrl, pedido);
  }

  obtenerMisPedidos(): Observable<Pedido[]> {
    return this.http.get<Pedido[]>(`${this.apiUrl}/mis-pedidos`);
  }

  obtenerPedido(id: number): Observable<Pedido> {
    return this.http.get<Pedido>(`${this.apiUrl}/${id}`);
  }

  listarTodosPedidos(): Observable<Pedido[]> {
    return this.http.get<Pedido[]>(this.apiUrl);
  }

  actualizarEstado(pedidoId: number, estado: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${pedidoId}/estado`, { estado });
  }
}