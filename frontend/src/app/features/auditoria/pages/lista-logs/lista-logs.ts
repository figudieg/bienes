import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { InventarioService } from '../../../../core/services/inventario.service';
import { mostrarErrorHttp } from '../../../../shared/utils/http-error.util';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-lista-logs',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './lista-logs.html',
  styleUrls: ['./lista-logs.css']
})
export class ListaLogsComponent implements OnInit {
  // 0: Dashboard, 1: Trazabilidad, 2: Conciliación, 3: Control Interno, 4: Depreciación, 5: Hallazgos
  seccionActiva: number = 0;
  
  cargando = true;
  logs: any[] = []; // Logs de Bienes generales

  // 1. Trazabilidad del Ciclo de Vida
  trazas: any[] = [];
  filteredTrazas: any[] = [];
  filtroTipoMovimiento: string = 'TODOS';
  searchTrazaQuery: string = '';

  // 2. Conciliación y Control Físico
  bienes: any[] = [];
  filteredBienes: any[] = [];
  searchConciliarQuery: string = '';
  filtroCotejo: string = 'TODOS';
  // Almacena localmente las conciliaciones realizadas en la sesión para dar feedback inmediato al 100%
  cotejosFisicos: Record<number, { fecha: Date, responsable: string, estado: string }> = {};

  // 3. Evaluación de Control Interno (Seguridad con IP y Hora exacta)
  accesos: any[] = [];
  filteredAccesos: any[] = [];
  searchAccesoQuery: string = '';

  // 4. Valoración y Depreciación (calculada en el servidor, a partir de la fecha real de adquisición)
  bienesDepreciacion: any[] = [];

  // 5. Hallazgos y Emisión de Informes
  hallazgos: any[] = [];
  cargandoHallazgos = false;
  nuevoHallazgo: any = {
    bien: null,
    descripcion: '',
    gravedad: 'MEDIA'
  };
  guardandoHallazgo = false;

  constructor(private inventarioService: InventarioService) {}

  ngOnInit() {
    this.cargarDatosDashboard();
  }

  cargarDatosDashboard() {
    this.cargando = true;
    this.inventarioService.getLogs().subscribe({
      next: (data: any[]) => {
        this.logs = data;
        this.cargando = false;
      },
      error: (err) => {
        this.cargando = false;
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudieron cargar los registros de auditoría.' });
      }
    });
  }

  cambiarSeccion(seccion: number) {
    this.seccionActiva = seccion;
    this.cargando = true;

    if (seccion === 0) {
      this.cargarDatosDashboard();
    } else if (seccion === 1) {
      // 1. Trazabilidad del Ciclo de Vida
      this.inventarioService.getTrazas().subscribe({
        next: (data: any[]) => {
          this.trazas = data;
          this.filtrarTrazas();
          this.cargando = false;
        },
        error: (err) => {
          this.cargando = false;
          mostrarErrorHttp(err, { mensajeFallback: 'No se pudo cargar la trazabilidad de bienes.' });
        }
      });
    } else if (seccion === 2 || seccion === 4) {
      // 2. Conciliación y 4. Depreciación (el valor y la depreciación ya vienen calculados desde el servidor)
      this.inventarioService.getBienes().subscribe({
        next: (data: any[]) => {
          this.bienes = data;
          this.bienesDepreciacion = data;
          this.filtrarBienesConciliacion();
          this.cargando = false;
        },
        error: (err) => {
          this.cargando = false;
          mostrarErrorHttp(err, { mensajeFallback: 'No se pudieron cargar los bienes para conciliación.' });
        }
      });
    } else if (seccion === 3) {
      // 3. Evaluación de Control Interno (Seguridad con IP)
      this.inventarioService.getAccesos().subscribe({
        next: (data: any[]) => {
          this.accesos = data;
          this.filtrarAccesos();
          this.cargando = false;
        },
        error: (err) => {
          this.cargando = false;
          mostrarErrorHttp(err, { mensajeFallback: 'No se pudo cargar la bitácora de accesos.' });
        }
      });
    } else if (seccion === 5) {
      // 5. Hallazgos: necesita el listado de bienes (para el selector) y los hallazgos reales
      this.cargarHallazgos();
      if (this.bienes.length === 0) {
        this.inventarioService.getBienes().subscribe({ next: (data: any[]) => this.bienes = data });
      }
      this.cargando = false;
    }
  }

  // --- MÉTODOS SUB-MENÚ 5: HALLAZGOS ---
  cargarHallazgos() {
    this.cargandoHallazgos = true;
    this.inventarioService.getHallazgos().subscribe({
      next: (data: any[]) => {
        this.hallazgos = data;
        this.cargandoHallazgos = false;
      },
      error: (err) => {
        this.cargandoHallazgos = false;
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudieron cargar los hallazgos de auditoría.' });
      }
    });
  }

  agregarHallazgo() {
    if (!this.nuevoHallazgo.bien || !this.nuevoHallazgo.descripcion?.trim()) {
      Swal.fire('Campos incompletos', 'Seleccione el bien afectado y describa el hallazgo.', 'warning');
      return;
    }
    this.guardandoHallazgo = true;
    this.inventarioService.crearHallazgo(this.nuevoHallazgo).subscribe({
      next: () => {
        this.guardandoHallazgo = false;
        this.nuevoHallazgo = { bien: null, descripcion: '', gravedad: 'MEDIA' };
        this.cargarHallazgos();
        Swal.fire({
          title: '¡Hallazgo Registrado!',
          text: 'El hallazgo quedó registrado y disponible en el Informe de Auditoría.',
          icon: 'success',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 3000
        });
      },
      error: (err) => {
        this.guardandoHallazgo = false;
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudo registrar el hallazgo.' });
      }
    });
  }

  resolverHallazgo(h: any) {
    Swal.fire({
      title: `Resolver hallazgo — ${h.bien_codigo}`,
      input: 'textarea',
      inputLabel: 'Observaciones de la resolución (opcional)',
      inputPlaceholder: 'Ej: Se localizó el bien, se corrigió el serial en el sistema...',
      showCancelButton: true,
      confirmButtonText: 'Marcar como resuelto',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (!result.isConfirmed) return;
      this.inventarioService.resolverHallazgo(h.id, result.value || '').subscribe({
        next: () => {
          this.cargarHallazgos();
          Swal.fire('Hallazgo resuelto', 'Se registró la resolución del hallazgo.', 'success');
        },
        error: (err) => mostrarErrorHttp(err, { mensajeFallback: 'No se pudo marcar el hallazgo como resuelto.' })
      });
    });
  }

  getGravedadBadge(gravedad: string): string {
    const map: Record<string, string> = { 'ALTA': 'danger', 'MEDIA': 'warning', 'BAJA': 'info' };
    return map[gravedad] || 'secondary';
  }

  getHallazgoEstadoBadge(estado: string): string {
    const map: Record<string, string> = { 'PENDIENTE': 'danger', 'EN_PROCESO': 'warning', 'RESUELTO': 'success' };
    return map[estado] || 'secondary';
  }

  // --- MÉTODOS SUB-MENÚ 1: TRAZABILIDAD ---
  filtrarTrazas() {
    this.filteredTrazas = this.trazas.filter(t => {
      const matchTipo = this.filtroTipoMovimiento === 'TODOS' || t.tipo_movimiento === this.filtroTipoMovimiento;
      const matchQuery = !this.searchTrazaQuery || 
        (t.bien_codigo || '').toLowerCase().includes(this.searchTrazaQuery.toLowerCase()) ||
        (t.bien_nombre || '').toLowerCase().includes(this.searchTrazaQuery.toLowerCase()) ||
        (t.motivo || '').toLowerCase().includes(this.searchTrazaQuery.toLowerCase());
      return matchTipo && matchQuery;
    });
  }

  getTipoMovimientoBadge(tipo: string): string {
    const map: Record<string, string> = {
      'INCORPORACION': 'success',
      'ASIGNACION': 'info',
      'REASIGNACION': 'warning',
      'DESINCORPORACION': 'danger'
    };
    return map[tipo] || 'secondary';
  }

  // --- MÉTODOS SUB-MENÚ 2: CONCILIACIÓN FÍSICA ---
  filtrarBienesConciliacion() {
    this.filteredBienes = this.bienes.filter(b => {
      const cotejoLocal = this.cotejosFisicos[b.id]?.estado ?? 'PENDIENTE';
      const matchCotejo = this.filtroCotejo === 'TODOS' || cotejoLocal === this.filtroCotejo;
      const matchQuery = !this.searchConciliarQuery || 
        (b.codigo_inventario || '').toLowerCase().includes(this.searchConciliarQuery.toLowerCase()) ||
        (b.nombre || '').toLowerCase().includes(this.searchConciliarQuery.toLowerCase()) ||
        (b.sede_nombre || '').toLowerCase().includes(this.searchConciliarQuery.toLowerCase());
      return matchCotejo && matchQuery;
    });
  }

  cotejarFisicamente(bien: any) {
    Swal.fire({
      title: 'Conciliación Física',
      html: `¿Confirmar cotejo físico de campo del bien <strong>${bien.codigo_inventario}</strong> (${bien.nombre})? <br><br> Se marcará como validado en la realidad física institucional.`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#2e7d32',
      cancelButtonColor: '#c62828',
      confirmButtonText: 'Sí, verificar físico',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        // Marcamos localmente como conciliado
        this.cotejosFisicos[bien.id] = {
          fecha: new Date(),
          responsable: 'María Auditora (Auditor/Especialista)',
          estado: 'CONCILIADO'
        };
        this.filtrarBienesConciliacion();
        
        Swal.fire(
          '¡Bien Conciliado!',
          'El cotejo físico ha sido registrado con éxito. Se confrontó el sistema con la realidad física.',
          'success'
        );
      }
    });
  }

  // --- MÉTODOS SUB-MENÚ 3: CONTROL INTERNO ---
  filtrarAccesos() {
    this.filteredAccesos = this.accesos.filter(a => {
      return !this.searchAccesoQuery || 
        (a.usuario_nombre || '').toLowerCase().includes(this.searchAccesoQuery.toLowerCase()) ||
        (a.usuario_nombre_completo || '').toLowerCase().includes(this.searchAccesoQuery.toLowerCase()) ||
        (a.ip_address || '').includes(this.searchAccesoQuery) ||
        (a.accion || '').toLowerCase().includes(this.searchAccesoQuery.toLowerCase());
    });
  }

  getAccesoAccionClass(accion: string): string {
    if (accion.includes('INICIO')) return 'success';
    if (accion.includes('CIERRE')) return 'secondary';
    if (accion.includes('MODIFICACION') || accion.includes('CAMBIO')) return 'warning';
    return 'info';
  }

  // --- MÉTODOS SUB-MENÚ 5: HALLAZGOS Y REPORTES ---
  descargarActaHallazgos() {
    Swal.fire({
      title: 'Emisión de Informe de Fiscalización',
      text: 'Se generará y descargará el Informe Oficial de Auditoría y Fiscalización de la DEM en formato PDF.',
      icon: 'info',
      showCancelButton: true,
      confirmButtonColor: '#2c3e50',
      confirmButtonText: 'Emitir y Descargar PDF',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        Swal.fire({
          title: 'Generando PDF...',
          text: 'Por favor espere mientras el servidor compila el reporte de fiscalización.',
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          }
        });

        this.inventarioService.descargarReporteAuditoriaPdf().subscribe({
          next: (blob: Blob) => {
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `Informe_Auditoria_Fiscalizacion_DEM.pdf`;
            link.click();
            window.URL.revokeObjectURL(url);
            Swal.fire('¡Informe Emitido!', 'El Informe Consolidado en PDF ha sido descargado.', 'success');
          },
          error: (err) => {
            mostrarErrorHttp(err, { mensajeFallback: 'No se pudo generar el reporte PDF en el servidor.' });
          }
        });
      }
    });
  }

  // Helper general badges de auditoría
  getAccionBadge(accion: string): string {
    const map: Record<string, string> = {
      'CREACION': 'success',
      'MODIFICACION': 'warning',
      'ASIGNACION': 'info',
      'DESINCORPORACION': 'danger'
    };
    return map[accion] || 'secondary';
  }
}
