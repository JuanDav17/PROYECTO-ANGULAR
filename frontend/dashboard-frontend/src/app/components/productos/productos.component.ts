// Pega este contenido en src/app/components/productos/productos.component.ts

import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface Producto {
  id?: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  cantidad: number;
}

@Component({
  selector: 'app-productos',
  templateUrl: './productos.component.html',
  styleUrls: ['./productos.component.scss']
})
export class ProductosComponent implements OnInit {
  productos: Producto[] = [];
  nuevoProducto: Producto = { nombre: '', descripcion: '', precio: 0, cantidad: 0 };

  private apiUrl = 'http://localhost:3000/productos'; 

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.obtenerProductos();
  }

  obtenerProductos() {
    this.http.get<Producto[]>(this.apiUrl).subscribe({
      next: (data) => (this.productos = data),
      error: (err) => console.error('Error al obtener productos:', err)
    });
  }

  agregarProducto() {
    this.http.post<Producto>(this.apiUrl, this.nuevoProducto).subscribe({
      next: (data) => {
        this.productos.push(data);
        this.nuevoProducto = { nombre: '', descripcion: '', precio: 0, cantidad: 0 };
      },
      error: (err) => console.error('Error al agregar producto:', err)
    });
  }

  editarProducto(producto: Producto) {
    // Pedir los nuevos valores, usando los actuales como predeterminados
    const nuevoNombre = prompt('Nuevo nombre:', producto.nombre);
    const nuevaDescripcion = prompt('Nueva descripción:', producto.descripcion || '');
    const nuevoPrecioStr = prompt('Nuevo precio:', producto.precio.toString());
    const nuevaCantidadStr = prompt('Nueva cantidad:', producto.cantidad.toString());

    // Comprobar si el usuario canceló
    if (nuevoNombre === null || nuevaDescripcion === null || nuevoPrecioStr === null || nuevaCantidadStr === null) {
      alert('Edición cancelada.');
      return;
    }

    // Conversión y validación de números
    const nuevoPrecio = parseFloat(nuevoPrecioStr);
    const nuevaCantidad = parseInt(nuevaCantidadStr, 10);

    if (isNaN(nuevoPrecio) || isNaN(nuevaCantidad) || nuevoPrecio < 0 || nuevaCantidad < 0) {
        alert('Error: Precio o cantidad inválidos.');
        return;
    }

    // Crear el objeto actualizado con todos los campos
    const actualizado = { 
        ...producto, 
        nombre: nuevoNombre,
        descripcion: nuevaDescripcion,
        precio: nuevoPrecio,
        cantidad: nuevaCantidad
    };

    // Enviar la solicitud PUT
    this.http.put(`${this.apiUrl}/${producto.id}`, actualizado).subscribe({
      next: () => {
          alert(`Producto "${nuevoNombre}" actualizado con éxito.`);
          this.obtenerProductos(); 
      },
      error: (err) => console.error('Error al editar producto:', err)
    });
  }

  eliminarProducto(id?: number) {
    if (!id || !confirm('¿Seguro que deseas eliminar este producto?')) return;
    this.http.delete(`${this.apiUrl}/${id}`).subscribe({
      next: () => this.obtenerProductos(),
      error: (err) => console.error('Error al eliminar producto:', err)
    });
  }
}