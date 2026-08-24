import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import { AuthService } from '../../../../core/services/auth.service';
import { GestionBienModalComponent } from '../../../../shared/components/gestion-bien-modal/gestion-bien-modal';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-lista-bienes',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, GestionBienModalComponent],
  templateUrl: './lista-bienes.html',
  styleUrls: ['./lista-bienes.css']
})
export class ListaBienesComponent implements OnInit {
  bienes: any[] = [];
  filteredBienes: any[] = [];
  filtroEstado: string = 'TODOS';
  filtroTipo: string = 'TODOS';
  filtroCategoria: string = 'TODAS';
  searchQuery: string = '';
  filtroOrden: string = '';
  cargando = true;
  isAdmin = false;

  bienModal: any = null;
  modoModal: 'reasignar' | 'desincorporar' | null = null;

  categorias = [
    { value: 'COMPUTADORA', label: 'Computadoras' },
    { value: 'PANTALLA', label: 'Pantallas' },
    { value: 'PERIFERICO', label: 'Periféricos (Mouse, Teclado, etc.)' },
    { value: 'MOBILIARIO', label: 'Mobiliario' },
    { value: 'EQUIPO_OFICINA', label: 'Equipo de Oficina' },
    { value: 'ELECTRODOMESTICO', label: 'Electrodomésticos' },
    { value: 'HERRAMIENTA', label: 'Herramientas' },
    { value: 'OTRO', label: 'Otro' },
  ];

  constructor(
    private inventarioService: InventarioService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.isAdmin = this.authService.hasRole('ADMINISTRADOR');
    this.inventarioService.getBienes().subscribe({
      next: (data: any[]) => {
        this.bienes = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error cargando bienes:', err);
        this.cargando = false;
      }
    });
  }

  aplicarFiltro() {
    // Al cambiar de tipo, la categoría (que solo aplica a MUEBLE) deja de tener sentido.
    if (this.filtroTipo !== 'MUEBLE' && this.filtroTipo !== 'TODOS') {
      this.filtroCategoria = 'TODAS';
    }
    this.filteredBienes = this.bienes.filter(bien => {
      if (!bien) return false;
      const matchEstado = this.filtroEstado === 'TODOS' || bien.estado === this.filtroEstado;
      const matchTipo = this.filtroTipo === 'TODOS' || bien.tipo === this.filtroTipo;
      const matchCategoria = this.filtroCategoria === 'TODAS' || bien.categoria === this.filtroCategoria;
      const searchQueryLower = (this.searchQuery || '').toLowerCase().trim();
      const matchSearch = !searchQueryLower ||
        (bien.nombre && bien.nombre.toLowerCase().includes(searchQueryLower)) ||
        (bien.codigo_inventario && bien.codigo_inventario.toLowerCase().includes(searchQueryLower)) ||
        (bien.serial_fabrica && bien.serial_fabrica.toLowerCase().includes(searchQueryLower));
      const filtroOrdenLower = (this.filtroOrden || '').toLowerCase().trim();
      const matchOrden = !filtroOrdenLower ||
        (bien.orden_compra_numero && bien.orden_compra_numero.toLowerCase().includes(filtroOrdenLower));
      return matchEstado && matchTipo && matchCategoria && matchSearch && matchOrden;
    });
  }

  getRutaEditar(bien: any): string[] {
    if (bien.tipo === 'AUTOMOTOR') return ['/automotor/editar', bien.id];
    if (bien.tipo === 'INMUEBLE') return ['/inmuebles/editar', bien.id];
    return ['/bienes/editar', bien.id];
  }

  irAAsignar(bien: any) {
    this.router.navigate(['/asignaciones/nueva'], { queryParams: { bienId: bien.id } });
  }

  abrirReasignar(bien: any) {
    this.bienModal = bien;
    this.modoModal = 'reasignar';
  }

  abrirDesincorporar(bien: any) {
    this.bienModal = bien;
    this.modoModal = 'desincorporar';
  }

  cerrarModal() {
    this.modoModal = null;
    this.bienModal = null;
  }

  onModalCompletado() {
    this.cerrarModal();
    this.cargando = true;
    this.inventarioService.getBienes().subscribe({
      next: (data: any[]) => {
        this.bienes = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: () => this.cargando = false
    });
  }

  eliminar(id: number, nombre: string) {
    Swal.fire({
      title: '¿Eliminar bien?',
      text: `Se eliminará permanentemente "${nombre}". Esta acción no se puede deshacer.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then(result => {
      if (result.isConfirmed) {
        this.inventarioService.deleteBien(id).subscribe({
          next: () => {
            this.bienes = this.bienes.filter(b => b.id !== id);
            this.aplicarFiltro();
            Swal.fire('Eliminado', 'El bien ha sido eliminado del inventario.', 'success');
          },
          error: () => Swal.fire('Error', 'No se pudo eliminar el bien. Puede tener asignaciones activas.', 'error')
        });
      }
    });
  }

  getEstadoBadge(estado: string): string {
    const map: Record<string, string> = {
      'ACTIVO': 'success', 'INACTIVO': 'warning', 'DESINCORPORADO': 'danger'
    };
    return map[estado] || 'secondary';
  }
}
