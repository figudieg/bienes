import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../core/services/inventario.service';
import { mostrarErrorHttp } from '../../../shared/utils/http-error.util';
import { PATRON_SOLO_LETRAS, PATRON_NOMBRE_CON_TITULO } from '../../../shared/utils/validadores-texto.util';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-reportes-bienes-publicos',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule],
  templateUrl: './reportes-bienes-publicos.html',
  styleUrls: ['./reportes-bienes-publicos.css']
})
export class ReportesBienesPublicosComponent implements OnInit {
  isUploading = false;
  uploadStatus: 'idle' | 'success' | 'error' = 'idle';
  uploadMessage = '';
  importedCount = 0;
  errors: string[] = [];

  // Lists
  bienesConOC: any[] = [];
  trazasReasignacion: any[] = [];
  mantenimientos: any[] = [];

  // Interactive Generator Lists
  bienes: any[] = [];
  filteredBienes: any[] = [];
  sedes: any[] = [];
  areas: any[] = [];
  filteredAreas: any[] = [];
  funcionarios: any[] = [];

  // Selections
  selectedBienes = new Set<number>();

  // Filters
  filtroSede: string = 'TODOS';
  filtroEstado: string = 'TODOS';
  filtroDireccionGeneral: string = 'TODOS';
  filtroArea: string = 'TODOS';
  filtroTipo: string = 'TODOS';
  searchQuery: string = '';
  direccionesGenerales: string[] = [];
  areasFiltroDisponibles: any[] = [];

  // Modals Visibility
  showReasignarModal = false;
  showDesincorporarModal = false;
  showMantenimientoModal = false;

  // Form Models
  reasignarForm = {
    sedeDestinoId: '',
    areaDestinoId: '',
    funcionarioDestinoId: '',
    motivo: '',
    cedenteNombre: '',
    receptorNombre: ''
  };

  desincorporarForm = {
    motivo: 'Deterioro físico y obsolescencia tecnológica'
  };

  mantenimientoForm = {
    numeroFicha: '',
    fechaFicha: '',
    tipoMantenimiento: 'CORRECTIVO',
    actividadRealizada: '',
    materialesEmpleados: '',
    numeroFactura: 'Autogestión',
    costo: 0.00,
    fechaMantenimiento: '',
    reparadoPor: 'Soporte Técnico DEM',
    conformadoPor: 'Jefe de Bienes DEM',
    responsableAdministrativo: 'Director de Administración DEM',
    nota: ''
  };

  selectedTab: 'incorporaciones' | 'reasignaciones' | 'mantenimientos' | 'generador' = 'generador';

  constructor(private inventarioService: InventarioService) {}

  ngOnInit(): void {
    this.loadData();
    this.initFormDates();
  }

  initFormDates(): void {
    const today = new Date().toISOString().substring(0, 10);
    this.mantenimientoForm.fechaFicha = today;
    this.mantenimientoForm.fechaMantenimiento = today;
  }

  loadData(): void {
    this.inventarioService.getBienes().subscribe({
      next: (data: any[]) => {
        this.bienes = data;
        this.bienesConOC = data.filter((b: any) => b.orden_compra !== null);
        this.aplicarFiltros();
      },
      error: (err) => console.error(err)
    });

    this.inventarioService.getTrazas().subscribe({
      next: (data) => {
        this.trazasReasignacion = data.filter((t: any) => t.tipo_movimiento === 'REASIGNACION');
      },
      error: (err) => console.error(err)
    });

    this.inventarioService.getMantenimientos().subscribe({
      next: (data) => {
        this.mantenimientos = data;
      },
      error: (err) => console.error(err)
    });

    this.inventarioService.getSedes().subscribe({
      next: (data) => {
        this.sedes = data;
      },
      error: (err) => console.error(err)
    });

    this.inventarioService.getAreas().subscribe({
      next: (data: any[]) => {
        this.areas = data.filter(a => a.activa !== false);
        this.direccionesGenerales = Array.from(
          new Set(this.areas.map(a => a.direccion_general).filter((d): d is string => !!d))
        ).sort();
        this.areasFiltroDisponibles = this.areas;
      },
      error: (err) => console.error(err)
    });

    this.inventarioService.getFuncionarios().subscribe({
      next: (data) => {
        this.funcionarios = data;
      },
      error: (err) => console.error(err)
    });
  }

  aplicarFiltros(): void {
    this.filteredBienes = this.bienes.filter(b => {
      const matchSede = this.filtroSede === 'TODOS' || b.sede === +this.filtroSede;
      const matchEstado = this.filtroEstado === 'TODOS' || b.estado === this.filtroEstado;
      const matchTipo = this.filtroTipo === 'TODOS' || b.tipo === this.filtroTipo;
      const matchDireccionGeneral = this.filtroDireccionGeneral === 'TODOS' ||
        b.asignacion_activa?.direccion_general === this.filtroDireccionGeneral;
      const matchArea = this.filtroArea === 'TODOS' || b.asignacion_activa?.area_id === +this.filtroArea;
      const matchSearch = !this.searchQuery ||
        b.nombre.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        b.codigo_inventario.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        (b.serial_fabrica && b.serial_fabrica.toLowerCase().includes(this.searchQuery.toLowerCase()));
      return matchSede && matchEstado && matchTipo && matchDireccionGeneral && matchArea && matchSearch;
    });

    // Clean selection of items no longer visible
    const visibleIds = new Set(this.filteredBienes.map(b => b.id));
    this.selectedBienes.forEach(id => {
      if (!visibleIds.has(id)) {
        this.selectedBienes.delete(id);
      }
    });
  }

  onFiltroDireccionGeneralChange(): void {
    this.filtroArea = 'TODOS';
    this.areasFiltroDisponibles = this.filtroDireccionGeneral === 'TODOS'
      ? this.areas
      : this.areas.filter(a => a.direccion_general === this.filtroDireccionGeneral);
    this.aplicarFiltros();
  }

  limpiarFiltros(): void {
    this.filtroSede = 'TODOS';
    this.filtroEstado = 'TODOS';
    this.filtroDireccionGeneral = 'TODOS';
    this.filtroArea = 'TODOS';
    this.filtroTipo = 'TODOS';
    this.searchQuery = '';
    this.areasFiltroDisponibles = this.areas;
    this.aplicarFiltros();
  }

  onSedeChange(sedeId: any): void {
    this.reasignarForm.areaDestinoId = '';
    if (sedeId) {
      this.filteredAreas = this.areas.filter(a => a.sede === +sedeId);
    } else {
      this.filteredAreas = [];
    }
  }

  // Checkbox helpers
  toggleSelectBien(bienId: number): void {
    if (this.selectedBienes.has(bienId)) {
      this.selectedBienes.delete(bienId);
    } else {
      this.selectedBienes.add(bienId);
    }
  }

  isBienSelected(bienId: number): boolean {
    return this.selectedBienes.has(bienId);
  }

  toggleSelectAll(event: any): void {
    const checked = event.target.checked;
    if (checked) {
      this.filteredBienes.forEach(b => this.selectedBienes.add(b.id));
    } else {
      this.filteredBienes.forEach(b => this.selectedBienes.delete(b.id));
    }
  }

  areAllSelected(): boolean {
    if (this.filteredBienes.length === 0) return false;
    return this.filteredBienes.every(b => this.selectedBienes.has(b.id));
  }

  // Drag & Drop / Upload
  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.uploadFile(file);
    }
  }

  onFileDropped(event: DragEvent): void {
    event.preventDefault();
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.uploadFile(event.dataTransfer.files[0]);
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  uploadFile(file: File): void {
    this.isUploading = true;
    this.uploadStatus = 'idle';
    this.uploadMessage = 'Procesando archivo...';
    this.errors = [];

    this.inventarioService.importarExcel(file).subscribe({
      next: (res) => {
        this.isUploading = false;
        this.uploadStatus = 'success';
        this.importedCount = res.imported_count;
        this.uploadMessage = `¡Importación exitosa! Se procesó el archivo como "${res.type_detected}".`;
        if (res.errors && res.errors.length > 0) {
          this.errors = res.errors;
        }
        this.loadData();
      },
      error: (err) => {
        this.isUploading = false;
        this.uploadStatus = 'error';
        if (err.status === 0 || err.status >= 500) {
          this.uploadMessage = 'No se pudo completar la importación por un problema de conexión o del servidor. Intente nuevamente.';
          return;
        }
        const serverError = (err.error && typeof err.error === 'object')
          ? (err.error?.error || err.error?.errors?.[0])
          : undefined;
        this.uploadMessage = `Error al importar: ${serverError || 'revise que el archivo tenga el formato correcto.'}`;
      }
    });
  }

  // Modal actions
  abrirReasignar(): void {
    if (this.selectedBienes.size === 0) {
      Swal.fire('Selección vacía', 'Debe seleccionar al menos un bien para reasignar.', 'warning');
      return;
    }
    this.reasignarForm = {
      sedeDestinoId: '',
      areaDestinoId: '',
      funcionarioDestinoId: '',
      motivo: 'Cambio de ubicación administrativa para adscripción operativa',
      cedenteNombre: 'María González (Analista de Inventario)',
      receptorNombre: ''
    };
    this.filteredAreas = [];
    this.showReasignarModal = true;
  }

  confirmarReasignacion(): void {
    if (!this.reasignarForm.sedeDestinoId || !this.reasignarForm.areaDestinoId || !this.reasignarForm.receptorNombre) {
      Swal.fire('Campos requeridos', 'Por favor, complete todos los campos obligatorios del formulario.', 'warning');
      return;
    }
    if (!PATRON_SOLO_LETRAS.test(this.reasignarForm.receptorNombre.trim())) {
      Swal.fire('Nombre inválido', 'El nombre del receptor solo debe contener letras y espacios.', 'warning');
      return;
    }
    if (this.reasignarForm.cedenteNombre && !PATRON_NOMBRE_CON_TITULO.test(this.reasignarForm.cedenteNombre.trim())) {
      Swal.fire('Nombre inválido', 'El nombre del cedente solo debe contener letras, espacios o signos comunes (. ( ) - ,).', 'warning');
      return;
    }

    Swal.fire({
      title: 'Generando Reasignación...',
      text: 'Por favor, espere mientras se procesan los activos y se compila el PDF.',
      allowOutsideClick: false,
      didOpen: () => Swal.showLoading()
    });

    const payload = {
      bien_ids: Array.from(this.selectedBienes),
      sede_destino_id: +this.reasignarForm.sedeDestinoId,
      area_destino_id: +this.reasignarForm.areaDestinoId,
      funcionario_destino_id: this.reasignarForm.funcionarioDestinoId ? +this.reasignarForm.funcionarioDestinoId : null,
      motivo: this.reasignarForm.motivo,
      cedente_nombre: this.reasignarForm.cedenteNombre,
      receptor_nombre: this.reasignarForm.receptorNombre
    };

    this.inventarioService.reasignarMasivo(payload).subscribe({
      next: (blob) => {
        this.showReasignarModal = false;
        this.selectedBienes.clear();
        this.saveBlob(blob, 'Comprobante_Reasignacion_Masiva.pdf');
        Swal.fire('¡Operación completada!', 'Los activos han sido reasignados y el comprobante oficial PDF ha sido descargado.', 'success');
        this.loadData();
      },
      error: (err) => {
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudo completar la reasignación en el servidor.' });
      }
    });
  }

  abrirDesincorporar(): void {
    if (this.selectedBienes.size === 0) {
      Swal.fire('Selección vacía', 'Debe seleccionar al menos un bien para desincorporar.', 'warning');
      return;
    }
    this.desincorporarForm = {
      motivo: 'Fallas técnicas mecánicas graves e irreparables (Deterioro u Obsolescencia)'
    };
    this.showDesincorporarModal = true;
  }

  confirmarDesincorporacion(): void {
    if (!this.desincorporarForm.motivo) {
      Swal.fire('Campos requeridos', 'Debe especificar el motivo de la desincorporación.', 'warning');
      return;
    }

    Swal.fire({
      title: 'Procesando Desincorporación...',
      text: 'Por favor, espere mientras se actualiza el estado físico de los activos.',
      allowOutsideClick: false,
      didOpen: () => Swal.showLoading()
    });

    const payload = {
      bien_ids: Array.from(this.selectedBienes),
      motivo: this.desincorporarForm.motivo
    };

    this.inventarioService.desincorporarMasivo(payload).subscribe({
      next: (blob) => {
        this.showDesincorporarModal = false;
        this.selectedBienes.clear();
        this.saveBlob(blob, 'Comprobante_Desincorporacion_Masiva.pdf');
        Swal.fire('¡Activos Desincorporados!', 'El estado de los bienes ha cambiado a Desincorporado y el reporte PDF ha sido descargado.', 'success');
        this.loadData();
      },
      error: (err) => {
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudo procesar la desincorporación masiva.' });
      }
    });
  }

  abrirMantenimiento(): void {
    if (this.selectedBienes.size === 0) {
      Swal.fire('Selección vacía', 'Debe seleccionar al menos un bien para el mantenimiento.', 'warning');
      return;
    }
    const today = new Date().toISOString().substring(0, 10);
    this.mantenimientoForm = {
      numeroFicha: `MANT-${Math.floor(1000 + Math.random() * 9000)}`,
      fechaFicha: today,
      tipoMantenimiento: 'CORRECTIVO',
      actividadRealizada: 'Limpieza física general, reemplazo de partes dañadas y pruebas de operatividad.',
      materialesEmpleados: 'Alcohol isopropílico, herramientas de precisión, pasta térmica.',
      numeroFactura: 'Autogestión',
      costo: 0.00,
      fechaMantenimiento: today,
      reparadoPor: 'Ing. Pedro Pérez (Soporte Técnico)',
      conformadoPor: 'María González (Jefe de Bienes DEM)',
      responsableAdministrativo: 'Director de Administración DEM',
      nota: 'Pruebas de funcionamiento post-servicio aprobadas al 100%.'
    };
    this.showMantenimientoModal = true;
  }

  confirmarMantenimiento(): void {
    if (!this.mantenimientoForm.numeroFicha || !this.mantenimientoForm.actividadRealizada || !this.mantenimientoForm.reparadoPor) {
      Swal.fire('Campos requeridos', 'Debe completar el número de ficha, actividad realizada y técnico responsable.', 'warning');
      return;
    }
    if (this.mantenimientoForm.costo < 0) {
      Swal.fire('Costo inválido', 'El costo del mantenimiento no puede ser negativo.', 'warning');
      return;
    }
    for (const [campo, valor] of [
      ['Técnico / reparado por', this.mantenimientoForm.reparadoPor],
      ['Conformado por', this.mantenimientoForm.conformadoPor],
      ['Responsable administrativo', this.mantenimientoForm.responsableAdministrativo],
    ] as const) {
      if (valor && !PATRON_NOMBRE_CON_TITULO.test(valor.trim())) {
        Swal.fire('Nombre inválido', `"${campo}" solo debe contener letras, espacios o signos comunes (. ( ) - ,).`, 'warning');
        return;
      }
    }

    Swal.fire({
      title: 'Registrando Mantenimiento...',
      text: 'Por favor, espere mientras se asocia el historial de reparaciones.',
      allowOutsideClick: false,
      didOpen: () => Swal.showLoading()
    });

    const payload = {
      bien_ids: Array.from(this.selectedBienes),
      numero_ficha: this.mantenimientoForm.numeroFicha,
      fecha_ficha: this.mantenimientoForm.fechaFicha,
      tipo_mantenimiento: this.mantenimientoForm.tipoMantenimiento,
      actividad_realizada: this.mantenimientoForm.actividadRealizada,
      materiales_empleados: this.mantenimientoForm.materialesEmpleados,
      numero_factura: this.mantenimientoForm.numeroFactura,
      costo: this.mantenimientoForm.costo,
      fecha_mantenimiento: this.mantenimientoForm.fechaMantenimiento,
      reparado_por: this.mantenimientoForm.reparadoPor,
      conformado_por: this.mantenimientoForm.conformadoPor,
      responsable_administrativo: this.mantenimientoForm.responsableAdministrativo,
      nota: this.mantenimientoForm.nota
    };

    this.inventarioService.mantenimientoMasivo(payload).subscribe({
      next: (blob) => {
        this.showMantenimientoModal = false;
        this.selectedBienes.clear();
        this.saveBlob(blob, `Ficha_Mantenimiento_Masiva_${this.mantenimientoForm.numeroFicha}.pdf`);
        Swal.fire('¡Mantenimiento Registrado!', 'El historial ha sido actualizado y la ficha en PDF ha sido descargada.', 'success');
        this.loadData();
      },
      error: (err) => {
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudo registrar el mantenimiento en el servidor.' });
      }
    });
  }

  // Download helpers
  downloadIncorporacionPdf(bienId: number): void {
    this.inventarioService.descargarComprobanteIncorporacionPdf(bienId).subscribe({
      next: (blob) => this.saveBlob(blob, `Comprobante_Incorporacion_${bienId}.pdf`),
      error: (err) => mostrarErrorHttp(err, { mensajeFallback: 'No se pudo descargar el comprobante.' })
    });
  }

  downloadReasignacionPdf(trazaId: number): void {
    this.inventarioService.descargarComprobanteReasignacionPdf(trazaId).subscribe({
      next: (blob) => this.saveBlob(blob, `Comprobante_Reasignacion_${trazaId}.pdf`),
      error: (err) => mostrarErrorHttp(err, { mensajeFallback: 'No se pudo descargar el comprobante.' })
    });
  }

  downloadMantenimientoPdf(mantId: number): void {
    this.inventarioService.descargarFichaMantenimientoPdf(mantId).subscribe({
      next: (blob) => this.saveBlob(blob, `Ficha_Mantenimiento_${mantId}.pdf`),
      error: (err) => mostrarErrorHttp(err, { mensajeFallback: 'No se pudo descargar la ficha.' })
    });
  }

  downloadInventarioGeneralPdf(): void {
    const filtros = {
      sede: this.filtroSede !== 'TODOS' ? this.filtroSede : '',
      estado: this.filtroEstado !== 'TODOS' ? this.filtroEstado : '',
      area: this.filtroArea !== 'TODOS' ? this.filtroArea : '',
      direccion_general: this.filtroArea === 'TODOS' && this.filtroDireccionGeneral !== 'TODOS' ? this.filtroDireccionGeneral : '',
      tipo: this.filtroTipo !== 'TODOS' ? this.filtroTipo : '',
      search: this.searchQuery || '',
    };
    const hayFiltros = Object.values(filtros).some(v => !!v);
    this.inventarioService.descargarInventarioGeneralPdf(filtros).subscribe({
      next: (blob) => this.saveBlob(blob, hayFiltros ? 'Reporte_Inventario_Filtrado.pdf' : 'Inventario_General_Bienes.pdf'),
      error: (err) => mostrarErrorHttp(err, { mensajeFallback: 'No se pudo descargar el inventario.' })
    });
  }

  private saveBlob(blob: Blob, fileName: string): void {
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = fileName;
    link.click();
    window.URL.revokeObjectURL(link.href);
  }
}
