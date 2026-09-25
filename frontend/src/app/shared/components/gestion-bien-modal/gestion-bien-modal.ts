import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../core/services/inventario.service';
import { mostrarErrorHttp } from '../../utils/http-error.util';
import { PATRON_SOLO_LETRAS } from '../../utils/validadores-texto.util';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-gestion-bien-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gestion-bien-modal.html'
})
export class GestionBienModalComponent implements OnChanges {
  @Input() bien: any = null;
  @Input() modo: 'reasignar' | 'desincorporar' | null = null;
  @Output() cerrar = new EventEmitter<void>();
  @Output() completado = new EventEmitter<void>();

  sedes: any[] = [];
  areas: any[] = [];
  filteredAreas: any[] = [];
  funcionarios: any[] = [];
  procesando = false;

  reasignarForm = { sedeDestinoId: '', areaDestinoId: '', funcionarioDestinoId: '', motivo: '', receptorNombre: '' };
  desincorporarForm = { motivo: '' };

  constructor(private inventarioService: InventarioService) {}

  get cedenteActual(): string | null {
    return this.bien?.asignacion_activa?.funcionario_nombre || null;
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['modo'] && this.modo) {
      this.reasignarForm = { sedeDestinoId: '', areaDestinoId: '', funcionarioDestinoId: '', motivo: '', receptorNombre: '' };
      this.desincorporarForm = { motivo: '' };
      this.filteredAreas = [];
      if (this.modo === 'reasignar') {
        this.inventarioService.getSedes().subscribe({ next: (d: any[]) => this.sedes = d });
        this.inventarioService.getAreas().subscribe({
          next: (d: any) => this.areas = (Array.isArray(d) ? d : (d.results || [])).filter((a: any) => a.activa !== false)
        });
        this.inventarioService.getFuncionarios().subscribe({ next: (d: any[]) => this.funcionarios = d });
      }
    }
  }

  onSedeChange() {
    this.reasignarForm.areaDestinoId = '';
    this.filteredAreas = this.reasignarForm.sedeDestinoId
      ? this.areas.filter(a => a.sede === +this.reasignarForm.sedeDestinoId)
      : [];
  }

  cerrarModal() {
    if (this.procesando) return;
    this.cerrar.emit();
  }

  confirmarReasignar() {
    if (!this.reasignarForm.sedeDestinoId || !this.reasignarForm.areaDestinoId || !this.reasignarForm.receptorNombre || !this.reasignarForm.motivo) {
      Swal.fire('Campos requeridos', 'Complete sede, área, receptor y motivo.', 'warning');
      return;
    }
    if (!PATRON_SOLO_LETRAS.test(this.reasignarForm.receptorNombre.trim())) {
      Swal.fire('Nombre inválido', 'El nombre del receptor solo debe contener letras y espacios.', 'warning');
      return;
    }
    this.procesando = true;
    const payload = {
      sede_destino_id: +this.reasignarForm.sedeDestinoId,
      area_destino_id: +this.reasignarForm.areaDestinoId,
      funcionario_destino_id: this.reasignarForm.funcionarioDestinoId ? +this.reasignarForm.funcionarioDestinoId : null,
      motivo: this.reasignarForm.motivo,
      cedente_nombre: this.cedenteActual || 'Depósito Central (bien sin asignación previa)',
      receptor_nombre: this.reasignarForm.receptorNombre,
    };
    this.inventarioService.reasignarBien(this.bien.id, payload).subscribe({
      next: (blob) => {
        this.procesando = false;
        this.saveBlob(blob, `Comprobante_Reasignacion_${this.bien.codigo_inventario}.pdf`);
        Swal.fire('¡Bien reasignado!', 'El comprobante oficial en PDF ha sido descargado.', 'success');
        this.completado.emit();
      },
      error: (err) => {
        this.procesando = false;
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudo completar la reasignación.' });
      }
    });
  }

  confirmarDesincorporar() {
    if (!this.desincorporarForm.motivo) {
      Swal.fire('Campo requerido', 'Debe indicar el motivo de la desincorporación.', 'warning');
      return;
    }
    this.procesando = true;
    this.inventarioService.desincorporarBien(this.bien.id, { motivo: this.desincorporarForm.motivo }).subscribe({
      next: (blob) => {
        this.procesando = false;
        this.saveBlob(blob, `Comprobante_Desincorporacion_${this.bien.codigo_inventario}.pdf`);
        Swal.fire('Bien desincorporado', 'El comprobante oficial en PDF ha sido descargado.', 'success');
        this.completado.emit();
      },
      error: (err) => {
        this.procesando = false;
        mostrarErrorHttp(err, { mensajeFallback: 'No se pudo completar la desincorporación.' });
      }
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
