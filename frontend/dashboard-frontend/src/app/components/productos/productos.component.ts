import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ProductoService } from '../../services/producto.service';
import { AuthService } from '../../services/auth.service';
import { Producto } from '../../models/producto.model';

@Component({
  selector: 'app-productos',
  templateUrl: './productos.component.html',
  styleUrls: ['./productos.component.scss']
})
export class ProductosComponent implements OnInit {
  productos: Producto[] = [];
  productosFiltrados: Producto[] = [];
  loading = false;
  error = '';
  searchTerm = '';

  // Para el modal de agregar/editar
  showModal = false;
  isEditMode = false;
  productoForm: Producto = this.getEmptyProducto();

  constructor(
    private productoService: ProductoService,
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cargarProductos();
  }

  get currentUser() {
    return this.authService.currentUserValue;
  }

  get isVendedor(): boolean {
    return this.authService.isVendedor;
  }

  get isAdmin(): boolean {
    return this.authService.isAdmin;
  }

  get canManageProducts(): boolean {
    return this.isVendedor || this.isAdmin;
  }

  cargarProductos(): void {
    this.loading = true;
    this.error = '';

    this.productoService.obtenerProductos().subscribe({
      next: (data) => {
        this.productos = data;
        this.productosFiltrados = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar productos:', err);
        this.error = 'Error al cargar productos';
        this.loading = false;
      }
    });
  }

  buscarProductos(): void {
    if (!this.searchTerm.trim()) {
      this.productosFiltrados = this.productos;
      return;
    }

    const term = this.searchTerm.toLowerCase();
    this.productosFiltrados = this.productos.filter(p => 
      p.nombre.toLowerCase().includes(term) ||
      (p.descripcion && p.descripcion.toLowerCase().includes(term))
    );
  }

  getEmptyProducto(): Producto {
    return {
      nombre: '',
      descripcion: '',
      precio: 0,
      cantidad: 0
    };
  }

  abrirModalAgregar(): void {
    this.isEditMode = false;
    this.productoForm = this.getEmptyProducto();
    this.showModal = true;
  }

  abrirModalEditar(producto: Producto): void {
    // Verificar permisos
    if (!this.puedeEditarProducto(producto)) {
      alert('No tienes permisos para editar este producto');
      return;
    }

    this.isEditMode = true;
    this.productoForm = { ...producto };
    this.showModal = true;
  }

  cerrarModal(): void {
    this.showModal = false;
    this.productoForm = this.getEmptyProducto();
  }

  guardarProducto(): void {
    if (!this.validarFormulario()) {
      return;
    }

    this.loading = true;

    if (this.isEditMode && this.productoForm.id) {
      // Actualizar
      this.productoService.actualizarProducto(this.productoForm.id, this.productoForm)
        .subscribe({
          next: () => {
            this.cerrarModal();
            this.cargarProductos();
            this.loading = false;
          },
          error: (err) => {
            console.error('Error al actualizar:', err);
            alert('Error al actualizar producto');
            this.loading = false;
          }
        });
    } else {
      // Crear
      this.productoService.agregarProducto(this.productoForm)
        .subscribe({
          next: () => {
            this.cerrarModal();
            this.cargarProductos();
            this.loading = false;
          },
          error: (err) => {
            console.error('Error al crear:', err);
            alert('Error al crear producto');
            this.loading = false;
          }
        });
    }
  }

  eliminarProducto(producto: Producto): void {
    if (!this.puedeEditarProducto(producto)) {
      alert('No tienes permisos para eliminar este producto');
      return;
    }

    if (!confirm(`¿Estás seguro de eliminar "${producto.nombre}"?`)) {
      return;
    }

    if (!producto.id) return;

    this.productoService.eliminarProducto(producto.id).subscribe({
      next: () => {
        this.cargarProductos();
      },
      error: (err) => {
        console.error('Error al eliminar:', err);
        alert('Error al eliminar producto');
      }
    });
  }

  puedeEditarProducto(producto: Producto): boolean {
    if (this.isAdmin) return true;
    if (this.isVendedor && producto.vendedor_id === this.currentUser?.id) return true;
    return false;
  }

  validarFormulario(): boolean {
    if (!this.productoForm.nombre.trim()) {
      alert('El nombre es requerido');
      return false;
    }
    if (this.productoForm.precio <= 0) {
      alert('El precio debe ser mayor a 0');
      return false;
    }
    if (this.productoForm.cantidad < 0) {
      alert('La cantidad no puede ser negativa');
      return false;
    }
    return true;
  }

  irAMisProductos(): void {
    this.router.navigate(['/vendedor/mis-productos']);
  }

  irADashboard(): void {
    if (this.isAdmin) {
      this.router.navigate(['/admin/dashboard']);
    } else if (this.isVendedor) {
      this.router.navigate(['/vendedor/dashboard']);
    } else {
      this.router.navigate(['/comprador/catalogo']);
    }
  }

  logout(): void {
    if (confirm('¿Deseas cerrar sesión?')) {
      this.authService.logout();
    }
  }
}