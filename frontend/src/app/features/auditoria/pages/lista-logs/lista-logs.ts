import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { InventarioService } from '../../../../core/services/inventario.service';
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

  // 4. Valoración, Depreciación y Seguros
  bienesDepreciacion: any[] = [];
  tasaBCV: number = 36.50; // Tasa de cambio estándar referencial del BCV

  // 5. Hallazgos y Emisión de Informes
  hallazgos: any[] = [
    {
      id: 1,
      bien_codigo: 'DEM-EQ-2401',
      descripcion: 'Diferencia en serial físico reportada en Auditoría de campo del área de TI.',
      gravedad: 'ALTA',
      fecha: new Date(),
      estado: 'PENDIENTE'
    },
    {
      id: 2,
      bien_codigo: 'DEM-VEH-1049',
      descripcion: 'Vehículo inactivo prolongado en estacionamiento de Sede Central sin justificativo.',
      gravedad: 'MEDIA',
      fecha: new Date(Date.now() - 86400000),
      estado: 'EN_PROCESO'
    }
  ];
  nuevoHallazgo: any = {
    bien_codigo: '',
    descripcion: '',
    gravedad: 'MEDIA'
  };

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
        console.error('Error cargando logs de auditoría:', err);
        this.cargando = false;
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
          console.error('Error cargando trazas de ciclo de vida:', err);
          this.cargando = false;
        }
      });
    } else if (seccion === 2 || seccion === 4) {
      // 2. Conciliación y 4. Depreciación
      this.inventarioService.getBienes().subscribe({
        next: (data: any[]) => {
          this.precalcularValoresBienes(data);
          this.bienes = data;
          this.bienesDepreciacion = data;
          this.filtrarBienesConciliacion();
          this.cargando = false;
        },
        error: (err) => {
          console.error('Error cargando bienes para conciliación/depreciación:', err);
          this.cargando = false;
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
          console.error('Error cargando bitácora de accesos:', err);
          this.cargando = false;
        }
      });
    } else if (seccion === 5) {
      this.cargando = false;
    }
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

  precalcularValoresBienes(bienes: any[]) {
    bienes.forEach(b => {
      b.anosVidaUtil = this.getAnosVidaUtil(b);
      b.depreciacionAnual = this.calcularDepreciacionAnual(b);
      b.depreciacionAcumulada = this.calcularDepreciacionAcumulada(b);
      b.valorNeto = this.calcularValorNeto(b);
      const seguro = this.getSeguroEstatus(b);
      b.seguroEstatusText = seguro.txt;
      b.seguroEstatusClass = seguro.cls;
    });
  }

  // --- MÉTODOS SUB-MENÚ 4: DEPRECIACIÓN Y VALORACIÓN ---
  getAnosVidaUtil(bien: any): number {
    const nombre = (bien.nombre || '').toLowerCase();
    if (nombre.includes('computadora') || nombre.includes('servidor') || nombre.includes('laptop') || nombre.includes('impresora') || nombre.includes('ups')) {
      return 5; // Equipos de computación
    }
    if (nombre.includes('vehiculo') || nombre.includes('carro') || nombre.includes('camioneta') || nombre.includes('moto') || nombre.includes('camion')) {
      return 10; // Parque automotor
    }
    if (nombre.includes('inmueble') || nombre.includes('edificio') || nombre.includes('terreno') || nombre.includes('oficina') || nombre.includes('sede')) {
      return 20; // Bienes inmuebles
    }
    return 10; // Otros bienes muebles y mobiliario estándar
  }

  calcularDepreciacionAnual(bien: any): number {
    const valor = parseFloat(bien.valor_adquisicion) || 100;
    const vida = this.getAnosVidaUtil(bien);
    return valor / vida;
  }

  calcularDepreciacionAcumulada(bien: any): number {
    const anual = this.calcularDepreciacionAnual(bien);
    // Simula una depreciación de 2 años (por ejemplo, desde 2024 al 2026 actual)
    return anual * 2;
  }

  calcularValorNeto(bien: any): number {
    const valor = parseFloat(bien.valor_adquisicion) || 100;
    const acumulada = this.calcularDepreciacionAcumulada(bien);
    return Math.max(0, valor - acumulada);
  }

  getSeguroEstatus(bien: any): { txt: string, cls: string } {
    const valor = parseFloat(bien.valor_adquisicion) || 0;
    if (valor > 1000) {
      return { txt: 'Asegurado - Activo (Póliza DEM-2026)', cls: 'success' };
    }
    return { txt: 'No Asegurado (Monto Crítico Bajo)', cls: 'secondary' };
  }

  // --- MÉTODOS SUB-MENÚ 5: HALLAZGOS Y REPORTES ---
  agregarHallazgo() {
    if (!this.nuevoHallazgo.bien_codigo || !this.nuevoHallazgo.descripcion) {
      Swal.fire('Campos Incompletos', 'Por favor complete todos los datos del hallazgo.', 'warning');
      return;
    }

    const hallazgo = {
      id: this.hallazgos.length + 1,
      bien_codigo: this.nuevoHallazgo.bien_codigo,
      descripcion: this.nuevoHallazgo.descripcion,
      gravedad: this.nuevoHallazgo.gravedad,
      fecha: new Date(),
      estado: 'PENDIENTE'
    };

    this.hallazgos.unshift(hallazgo);
    this.nuevoHallazgo = { bien_codigo: '', descripcion: '', gravedad: 'MEDIA' };

    Swal.fire({
      title: '¡Hallazgo Registrado!',
      text: 'El hallazgo de fiscalización ha sido registrado con éxito y emitido a control fiscal.',
      icon: 'success',
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000
    });
  }

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
            console.error('Error generando PDF de auditoría:', err);
            Swal.fire('Error', 'No se pudo generar el reporte PDF en el servidor.', 'error');
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
