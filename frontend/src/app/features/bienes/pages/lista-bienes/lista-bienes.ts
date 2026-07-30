import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import { AuthService } from '../../../../core/services/auth.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-lista-bienes',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './lista-bienes.html',
  styleUrls: ['./lista-bienes.css']
})
export class ListaBienesComponent implements OnInit {
  bienes: any[] = [];
  filteredBienes: any[] = [];
  filtroEstado: string = 'TODOS';
  searchQuery: string = '';
  filtroOrden: string = '';
  cargando = true;
  isAdmin = false;

  constructor(
    private inventarioService: InventarioService,
    private authService: AuthService
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
    this.filteredBienes = this.bienes.filter(bien => {
      if (!bien) return false;
      const matchEstado = this.filtroEstado === 'TODOS' || bien.estado === this.filtroEstado;
      const searchQueryLower = (this.searchQuery || '').toLowerCase().trim();
      const matchSearch = !searchQueryLower ||
        (bien.nombre && bien.nombre.toLowerCase().includes(searchQueryLower)) ||
        (bien.codigo_inventario && bien.codigo_inventario.toLowerCase().includes(searchQueryLower)) ||
        (bien.serial_fabrica && bien.serial_fabrica.toLowerCase().includes(searchQueryLower));
      const filtroOrdenLower = (this.filtroOrden || '').toLowerCase().trim();
      const matchOrden = !filtroOrdenLower ||
        (bien.orden_compra_numero && bien.orden_compra_numero.toLowerCase().includes(filtroOrdenLower));
      return matchEstado && matchSearch && matchOrden;
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
