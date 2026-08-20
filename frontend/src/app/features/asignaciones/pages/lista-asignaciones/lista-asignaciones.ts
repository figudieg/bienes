import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import { AuthService } from '../../../../core/services/auth.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-lista-asignaciones',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './lista-asignaciones.html',
  styleUrls: ['./lista-asignaciones.css']
})
export class ListaAsignacionesComponent implements OnInit {
  asignaciones: any[] = [];
  filteredAsignaciones: any[] = [];
  searchQuery: string = '';
  cargando = true;
  isAdmin = false;

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

  eliminar(id: number, bienCodigo: string) {
    Swal.fire({
      title: '¿Eliminar asignación?',
      text: `Se eliminará la asignación del bien ${bienCodigo}.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then(result => {
      if (result.isConfirmed) {
        this.inventarioService.deleteAsignacion(id).subscribe({
          next: () => {
            this.asignaciones = this.asignaciones.filter(a => a.id !== id);
            this.aplicarFiltro();
            Swal.fire('Eliminada', 'La asignación ha sido eliminada.', 'success');
          },
          error: () => Swal.fire('Error', 'No se pudo eliminar la asignación.', 'error')
        });
      }
    });
  }
}
