import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import Swal from 'sweetalert2';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-lista-ordenes',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, FormsModule],
  templateUrl: './lista-ordenes.html',
  styleUrls: ['./lista-ordenes.css']
})
export class ListaOrdenesComponent implements OnInit {
  ordenes: any[] = [];
  filteredOrdenes: any[] = [];
  searchQuery = '';
  cargando = true;
  descargando: number | null = null;
  
  mostrarModal = false;
  form!: FormGroup;
  archivoSeleccionado: File | null = null;
  guardando = false;

  constructor(
    private inventarioService: InventarioService,
    private fb: FormBuilder
  ) {}

  ngOnInit() {
    this.form = this.fb.group({
      numero_orden: ['', Validators.required],
      proveedor: [''],
      fecha_llegada: ['', Validators.required],
      conformidad_recepcion: [false]
    });
    this.cargarOrdenes();
  }

  cargarOrdenes() {
    this.cargando = true;
    this.inventarioService.getOrdenes().subscribe({
      next: (data: any[]) => {
        this.ordenes = data;
        this.aplicarFiltro();
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error cargando órdenes:', err);
        this.cargando = false;
      }
    });
  }

  aplicarFiltro() {
    if (!this.searchQuery) {
      this.filteredOrdenes = this.ordenes;
    } else {
      const query = this.searchQuery.toLowerCase().trim();
      this.filteredOrdenes = this.ordenes.filter(o => {
        return (o.numero_orden && o.numero_orden.toLowerCase().includes(query)) ||
               (o.fecha_llegada && o.fecha_llegada.toLowerCase().includes(query)) ||
               (o.proveedor && o.proveedor.toLowerCase().includes(query));
      });
    }
  }

  abrirModal() {
    this.form.reset({ conformidad_recepcion: false });
    this.archivoSeleccionado = null;
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
  }

  onFileChange(event: any) {
    if (event.target.files.length > 0) {
      this.archivoSeleccionado = event.target.files[0];
    }
  }

  guardarOrden() {
    if (this.form.invalid || !this.archivoSeleccionado) {
      this.form.markAllAsTouched();
      if (!this.archivoSeleccionado) {
        Swal.fire('Falta el documento', 'Debe adjuntar el documento de la orden de compra como soporte antes de cargarla.', 'warning');
      }
      return;
    }

    this.guardando = true;
    const formData = new FormData();
    formData.append('numero_orden', this.form.get('numero_orden')?.value);
    formData.append('proveedor', this.form.get('proveedor')?.value || 'Dirección Ejecutiva de la Magistratura (DEM)');
    formData.append('fecha_llegada', this.form.get('fecha_llegada')?.value);
    formData.append('conformidad_recepcion', this.form.get('conformidad_recepcion')?.value ? 'true' : 'false');
    formData.append('archivo_documento', this.archivoSeleccionado);

    this.inventarioService.createOrdenCompra(formData).subscribe({
      next: () => {
        this.guardando = false;
        this.cerrarModal();
        Swal.fire('¡Éxito!', 'Orden de compra cargada correctamente.', 'success');
        this.cargarOrdenes();
      },
      error: (err) => {
        this.guardando = false;
        console.error('Error guardando orden:', err);
        Swal.fire('Error', 'Ocurrió un error al registrar la orden.', 'error');
      }
    });
  }

  descargarPdf(orden: any) {
    this.descargando = orden.id;
    this.inventarioService.descargarReporteOrdenPdf(orden.id).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Reporte_Orden_${orden.numero_orden}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
        this.descargando = null;
      },
      error: (err) => {
        console.error('Error descargando PDF:', err);
        this.descargando = null;
      }
    });
  }

  verDocumento(orden: any) {
    if (orden.archivo_documento) {
      window.open(orden.archivo_documento, '_blank');
    }
  }
}
