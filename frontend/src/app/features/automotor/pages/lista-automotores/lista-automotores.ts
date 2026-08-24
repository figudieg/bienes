import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import { AuthService } from '../../../../core/services/auth.service';
import { GestionBienModalComponent } from '../../../../shared/components/gestion-bien-modal/gestion-bien-modal';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-lista-automotores',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, GestionBienModalComponent],
  templateUrl: './lista-automotores.html',
  styleUrls: ['./lista-automotores.css']
})
export class ListaAutomotoresComponent implements OnInit {
  automotores: any[] = [];
  filteredAutomotores: any[] = [];
  filtroEstado: string = 'TODOS';
  searchQuery: string = '';
  cargando = true;
  isAdmin = false;

  bienModal: any = null;
  modoModal: 'reasignar' | 'desincorporar' | null = null;

  constructor(
    private inventarioService: InventarioService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.isAdmin = this.authService.hasRole('ADMINISTRADOR');
    this.inventarioService.getAutomotores().subscribe({
      next: (data: any[]) => {
        this.automotores = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error cargando automotores:', err);
        this.cargando = false;
      }
    });
  }

  aplicarFiltro() {
    let list = this.automotores;
    if (this.filtroEstado !== 'TODOS') {
      list = list.filter(a => a.estado === this.filtroEstado);
    }
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase().trim();
      list = list.filter(a =>
        (a.codigo_inventario && a.codigo_inventario.toLowerCase().includes(query)) ||
        (a.placa && a.placa.toLowerCase().includes(query)) ||
        (a.marca && a.marca.toLowerCase().includes(query)) ||
        (a.modelo && a.modelo.toLowerCase().includes(query)) ||
        (a.color && a.color.toLowerCase().includes(query)) ||
        (a.serial_motor && a.serial_motor.toLowerCase().includes(query)) ||
        (a.serial_carroceria && a.serial_carroceria.toLowerCase().includes(query)) ||
        (a.sede_nombre && a.sede_nombre.toLowerCase().includes(query))
      );
    }
    this.filteredAutomotores = list;
  }

  eliminar(id: number, placa: string) {
    Swal.fire({
      title: '¿Eliminar automotor?',
      text: `Se eliminará permanentemente el vehículo con placa ${placa}.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then(result => {
      if (result.isConfirmed) {
        this.inventarioService.deleteAutomotor(id).subscribe({
          next: () => {
            this.automotores = this.automotores.filter(a => a.id !== id);
            this.aplicarFiltro();
            Swal.fire('Eliminado', 'El automotor ha sido eliminado.', 'success');
          },
          error: () => Swal.fire('Error', 'No se pudo eliminar el automotor.', 'error')
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

  irAAsignar(auto: any) {
    this.router.navigate(['/asignaciones/nueva'], { queryParams: { bienId: auto.id } });
  }

  abrirReasignar(auto: any) {
    this.bienModal = auto;
    this.modoModal = 'reasignar';
  }

  abrirDesincorporar(auto: any) {
    this.bienModal = auto;
    this.modoModal = 'desincorporar';
  }

  cerrarModal() {
    this.modoModal = null;
    this.bienModal = null;
  }

  onModalCompletado() {
    this.cerrarModal();
    this.cargando = true;
    this.inventarioService.getAutomotores().subscribe({
      next: (data: any[]) => {
        this.automotores = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: () => this.cargando = false
    });
  }
}
