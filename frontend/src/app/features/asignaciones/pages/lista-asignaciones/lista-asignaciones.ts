import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import { AuthService } from '../../../../core/services/auth.service';
import { GestionBienModalComponent } from '../../../../shared/components/gestion-bien-modal/gestion-bien-modal';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-lista-asignaciones',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, GestionBienModalComponent],
  templateUrl: './lista-asignaciones.html',
  styleUrls: ['./lista-asignaciones.css']
})
export class ListaAsignacionesComponent implements OnInit {
  asignaciones: any[] = [];
  filteredAsignaciones: any[] = [];
  searchQuery: string = '';
  cargando = true;
  isAdmin = false;

  bienModal: any = null;
  modoModal: 'reasignar' | 'desincorporar' | null = null;

  constructor(
    private inventarioService: InventarioService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.isAdmin = this.authService.hasRole('ADMINISTRADOR');
    this.inventarioService.getAsignaciones().subscribe({
      next: (data: any[]) => {
        this.asignaciones = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error cargando asignaciones:', err);
        this.cargando = false;
      }
    });
  }

  aplicarFiltro() {
    if (!this.searchQuery) {
      this.filteredAsignaciones = this.asignaciones;
    } else {
      const query = this.searchQuery.toLowerCase().trim();
      this.filteredAsignaciones = this.asignaciones.filter(asig =>
        (asig.bien_codigo && asig.bien_codigo.toLowerCase().includes(query)) ||
        (asig.funcionario_cedula && asig.funcionario_cedula.toLowerCase().includes(query)) ||
        (asig.funcionario_nombre && asig.funcionario_nombre.toLowerCase().includes(query)) ||
        (asig.area_nombre && asig.area_nombre.toLowerCase().includes(query))
      );
    }
  }

  eliminar(asig: any) {
    const titulo = asig.activa
      ? '¿Eliminar asignación activa?'
      : '¿Eliminar asignación?';
    const texto = asig.activa
      ? `El bien ${asig.bien_codigo} está actualmente asignado a ${asig.funcionario_nombre}. ` +
        `Eliminar el registro no genera trazabilidad. ` +
        `Se recomienda usar "Reasignar" o "Desincorporar" en su lugar. ¿Desea eliminarlo de todas formas?`
      : `Se eliminará el registro histórico de asignación del bien ${asig.bien_codigo}.`;

    Swal.fire({
      title: titulo,
      text: texto,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then(result => {
      if (result.isConfirmed) {
        this.inventarioService.deleteAsignacion(asig.id).subscribe({
          next: () => {
            this.asignaciones = this.asignaciones.filter(a => a.id !== asig.id);
            this.aplicarFiltro();
            Swal.fire('Eliminada', 'La asignación ha sido eliminada.', 'success');
          },
          error: () => Swal.fire('Error', 'No se pudo eliminar la asignación.', 'error')
        });
      }
    });
  }

  abrirReasignar(asig: any) {
    this.bienModal = this.bienDesdeAsignacion(asig);
    this.modoModal = 'reasignar';
  }

  abrirDesincorporar(asig: any) {
    this.bienModal = this.bienDesdeAsignacion(asig);
    this.modoModal = 'desincorporar';
  }

  private bienDesdeAsignacion(asig: any) {
    return {
      id: asig.bien,
      codigo_inventario: asig.bien_codigo,
      nombre: asig.bien_nombre,
      asignacion_activa: asig.activa ? { funcionario_nombre: asig.funcionario_nombre } : null,
    };
  }

  cerrarModal() {
    this.modoModal = null;
    this.bienModal = null;
  }

  onModalCompletado() {
    this.cerrarModal();
    this.cargando = true;
    this.inventarioService.getAsignaciones().subscribe({
      next: (data: any[]) => {
        this.asignaciones = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: () => this.cargando = false
    });
  }
}
