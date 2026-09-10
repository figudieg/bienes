import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-registro-inmueble',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './registro-inmueble.html',
  styleUrls: ['./registro-inmueble.css']
})
export class RegistroInmuebleComponent implements OnInit {
  inmueble: any = {
    nombre: '',
    descripcion: '',
    serial_fabrica: '',
    codigo_inventario: '',
    estado: 'ACTIVO',
    sede: null,
    orden_compra: null,
    direccion_completa: '',
    registro_propiedad: '',
    area_terreno: 0.00,
    area_construccion: 0.00,
    catastro: '',
    valor_adquisicion: 0.00
  };

  sedes: any[] = [];
  ordenes: any[] = [];
  guardando = false;
  editando = false;
  editId: number | null = null;

  constructor(
    private inventarioService: InventarioService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.inventarioService.getSedes().subscribe(data => this.sedes = data);
    this.inventarioService.getOrdenes().subscribe(data => this.ordenes = data);

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.editando = true;
      this.editId = +id;
      this.inventarioService.getInmueble(this.editId).subscribe({
        next: (data: any) => { this.inmueble = data; },
        error: () => Swal.fire('Error', 'No se pudo cargar el inmueble.', 'error')
      });
    } else {
      const num = Math.floor(Math.random() * 9000) + 1000;
      this.inmueble.codigo_inventario = `DEM-INM-${num}`;
    }
  }

  onSubmit() {
    if (!this.inmueble.catastro?.trim() || !this.inmueble.direccion_completa?.trim()) {
      Swal.fire('Campos obligatorios', 'Catastro y dirección completa son obligatorios.', 'warning');
      return;
    }
    if (!this.inmueble.sede) {
      Swal.fire('Campos obligatorios', 'Debe seleccionar una sede administrativa.', 'warning');
      return;
    }
    if (this.inmueble.area_terreno <= 0) {
      Swal.fire('Error de Validación', 'El área del terreno debe ser mayor que cero.', 'warning');
      return;
    }
    if (this.inmueble.area_construccion <= 0) {
      Swal.fire('Error de Validación', 'El área de construcción debe ser mayor que cero.', 'warning');
      return;
    }
    if (this.inmueble.valor_adquisicion < 0) {
      Swal.fire('Error de Validación', 'El valor de adquisición no puede ser negativo.', 'warning');
      return;
    }

    this.guardando = true;
    this.inmueble.nombre = `Inmueble Catastro: ${this.inmueble.catastro}`;
    this.inmueble.descripcion = `Bien Inmueble de la DEM. Ficha Catastral: ${this.inmueble.catastro}. Registro: ${this.inmueble.registro_propiedad}. Área Terreno: ${this.inmueble.area_terreno}m²`;

    const request = this.editando
      ? this.inventarioService.updateInmueble(this.editId!, this.inmueble)
      : this.inventarioService.createInmueble(this.inmueble);

    request.subscribe({
      next: () => {
        Swal.fire({
          title: this.editando ? '¡Inmueble Actualizado!' : '¡Inmueble Incorporado!',
          text: this.editando
            ? 'Los datos del inmueble han sido actualizados.'
            : 'El bien inmueble ha sido registrado exitosamente.',
          icon: 'success',
          confirmButtonColor: '#2c3e50'
        });
        this.router.navigate(['/inmuebles']);
      },
      error: (err) => {
        console.error('Error:', err);
        const errorMsg = err.error?.area_terreno?.[0] || err.error?.area_construccion?.[0]
          || err.error?.valor_adquisicion?.[0]
          || 'No se pudo guardar el inmueble. Verifique que el número catastral o folio no estén repetidos.';
        Swal.fire({ title: 'Error de Registro', text: errorMsg, icon: 'error', confirmButtonColor: '#2c3e50' });
        this.guardando = false;
      }
    });
  }
}
