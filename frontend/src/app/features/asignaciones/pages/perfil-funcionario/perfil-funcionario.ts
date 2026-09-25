import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { InventarioService } from '../../../../core/services/inventario.service';
import { GestionBienModalComponent } from '../../../../shared/components/gestion-bien-modal/gestion-bien-modal';
import { PATRON_SOLO_DIGITOS } from '../../../../shared/utils/validadores-texto.util';
import { mostrarErrorHttp } from '../../../../shared/utils/http-error.util';

@Component({
  selector: 'app-perfil-funcionario',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, GestionBienModalComponent],
  templateUrl: './perfil-funcionario.html',
  styleUrls: ['./perfil-funcionario.css']
})
export class PerfilFuncionarioComponent implements OnInit {
  cedula = '';
  buscando = false;
  error = '';
  funcionario: any = null;
  funcionarioId: number | null = null;
  bienes: any[] = [];
  totalBienes = 0;

  bienModal: any = null;
  modoModal: 'reasignar' | 'desincorporar' | null = null;

  constructor(
    private inventarioService: InventarioService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    const qp = this.route.snapshot.queryParamMap;
    const funcionarioId = qp.get('funcionarioId');
    const cedula = qp.get('cedula');
    if (funcionarioId) {
      this.cargarPerfil(+funcionarioId);
    } else if (cedula) {
      this.cedula = cedula;
      this.buscar();
    }
  }

  buscar() {
    const cedula = this.cedula.trim();
    if (!cedula || cedula.length < 6 || !PATRON_SOLO_DIGITOS.test(cedula)) {
      this.error = 'Ingrese un número de cédula válido (solo dígitos, mínimo 6).';
      return;
    }

    this.buscando = true;
    this.error = '';
    this.funcionario = null;
    this.bienes = [];

    this.inventarioService.consultarCedulaSiscom(cedula).subscribe({
      next: (data: any) => this.cargarPerfil(data.funcionario_id),
      error: (err) => {
        // Si SISCOM no responde (por ejemplo, fuera de la red del DEM), se
        // intenta con el directorio local de funcionarios ya conocidos.
        this.inventarioService.buscarFuncionarioLocal(cedula).subscribe({
          next: (data: any) => this.cargarPerfil(data.id),
          error: () => {
            this.buscando = false;
            if (err.status === 502) {
              this.error = 'No se pudo conectar con el sistema de RRHH (SISCOM) y este funcionario tampoco está registrado localmente.';
            } else if (err.status === 404) {
              this.error = err.error?.error || `No se encontró un funcionario con la cédula ${cedula}.`;
            } else {
              this.error = 'Error al consultar el funcionario. Intente nuevamente.';
            }
          }
        });
      }
    });
  }

  cargarPerfil(funcionarioId: number) {
    this.funcionarioId = funcionarioId;
    this.inventarioService.getFuncionarioPerfil(funcionarioId).subscribe({
      next: (data: any) => {
        this.buscando = false;
        this.funcionario = data.funcionario;
        this.bienes = data.bienes;
        this.totalBienes = data.total_bienes;
      },
      error: (err) => {
        this.buscando = false;
        if (err?.status === 0 || err?.status >= 500) return; // el interceptor global ya avisó
        this.error = 'No se pudo cargar el perfil del funcionario. Intente nuevamente.';
      }
    });
  }

  abrirReasignar(b: any) {
    this.bienModal = this.bienDesdePerfil(b);
    this.modoModal = 'reasignar';
  }

  abrirDesincorporar(b: any) {
    this.bienModal = this.bienDesdePerfil(b);
    this.modoModal = 'desincorporar';
  }

  private bienDesdePerfil(b: any) {
    return {
      id: b.bien_id,
      codigo_inventario: b.codigo_inventario,
      nombre: b.nombre,
      asignacion_activa: this.funcionario
        ? { funcionario_nombre: `${this.funcionario.nombres} ${this.funcionario.apellidos}` }
        : null,
    };
  }

  cerrarModal() {
    this.modoModal = null;
    this.bienModal = null;
  }

  onModalCompletado() {
    this.cerrarModal();
    if (this.funcionarioId) {
      this.cargarPerfil(this.funcionarioId);
    }
  }

  limpiar() {
    this.cedula = '';
    this.funcionario = null;
    this.funcionarioId = null;
    this.bienes = [];
    this.error = '';
  }

  getTipoIcon(tipo: string): string {
    if (tipo === 'Automotor') return 'fa-car';
    if (tipo === 'Inmueble') return 'fa-building';
    return 'fa-box';
  }

  getEstadoBadge(estado: string): string {
    const map: Record<string, string> = {
      'ACTIVO': 'success', 'INACTIVO': 'warning', 'DESINCORPORADO': 'danger'
    };
    return map[estado] || 'secondary';
  }
}
