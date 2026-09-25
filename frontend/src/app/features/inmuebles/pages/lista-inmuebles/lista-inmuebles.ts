import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import { AuthService } from '../../../../core/services/auth.service';
import { GestionBienModalComponent } from '../../../../shared/components/gestion-bien-modal/gestion-bien-modal';
import { mostrarErrorHttp } from '../../../../shared/utils/http-error.util';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-lista-inmuebles',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, GestionBienModalComponent],
  templateUrl: './lista-inmuebles.html',
  styleUrls: ['./lista-inmuebles.css']
})
export class ListaInmueblesComponent implements OnInit {
  inmuebles: any[] = [];
  filteredInmuebles: any[] = [];
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
    this.inventarioService.getInmuebles().subscribe({
      next: (data: any[]) => {
        this.inmuebles = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: (err) => {
        this.cargando = false;
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudieron cargar los inmuebles. Recargue la página.' });
      }
    });
  }

  aplicarFiltro() {
    let list = this.inmuebles;
    if (this.filtroEstado !== 'TODOS') {
      list = list.filter(i => i.estado === this.filtroEstado);
    }
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase().trim();
      list = list.filter(i =>
        (i.codigo_inventario && i.codigo_inventario.toLowerCase().includes(query)) ||
        (i.catastro && i.catastro.toLowerCase().includes(query)) ||
        (i.registro_propiedad && i.registro_propiedad.toLowerCase().includes(query)) ||
        (i.direccion_completa && i.direccion_completa.toLowerCase().includes(query)) ||
        (i.sede_nombre && i.sede_nombre.toLowerCase().includes(query))
      );
    }
    this.filteredInmuebles = list;
  }

  eliminar(id: number, catastro: string) {
    Swal.fire({
      title: '¿Eliminar inmueble?',
      text: `Se eliminará permanentemente el inmueble con catastro ${catastro}.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then(result => {
      if (result.isConfirmed) {
        this.inventarioService.deleteInmueble(id).subscribe({
          next: () => {
            this.inmuebles = this.inmuebles.filter(i => i.id !== id);
            this.aplicarFiltro();
            Swal.fire('Eliminado', 'El inmueble ha sido eliminado.', 'success');
          },
          error: (err) => mostrarErrorHttp(err, { mensajeFallback: 'No se pudo eliminar el inmueble.' })
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

  irAAsignar(inm: any) {
    this.router.navigate(['/asignaciones/nueva'], { queryParams: { bienId: inm.id } });
  }

  abrirReasignar(inm: any) {
    this.bienModal = inm;
    this.modoModal = 'reasignar';
  }

  abrirDesincorporar(inm: any) {
    this.bienModal = inm;
    this.modoModal = 'desincorporar';
  }

  cerrarModal() {
    this.modoModal = null;
    this.bienModal = null;
  }

  onModalCompletado() {
    this.cerrarModal();
    this.cargando = true;
    this.inventarioService.getInmuebles().subscribe({
      next: (data: any[]) => {
        this.inmuebles = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: () => this.cargando = false
    });
  }
}
