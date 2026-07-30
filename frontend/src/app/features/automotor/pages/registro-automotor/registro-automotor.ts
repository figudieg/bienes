import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { InventarioService } from '../../../../core/services/inventario.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-registro-automotor',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './registro-automotor.html',
  styleUrls: ['./registro-automotor.css']
})
export class RegistroAutomotorComponent implements OnInit {
  vehiculo: any = {
    nombre: '',
    descripcion: '',
    serial_fabrica: '',
    codigo_inventario: '',
    estado: 'ACTIVO',
    sede: null,
    orden_compra: null,
    placa: '',
    marca: '',
    modelo: '',
    anio: new Date().getFullYear(),
    color: '',
    serial_motor: '',
    serial_carroceria: '',
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
      this.inventarioService.getAutomotor(this.editId).subscribe({
        next: (data: any) => { this.vehiculo = data; },
        error: () => Swal.fire('Error', 'No se pudo cargar el automotor.', 'error')
      });
    } else {
      const num = Math.floor(Math.random() * 90000) + 10000;
      this.vehiculo.codigo_inventario = `DEM-VEH-${num}`;
    }
  }

  onSubmit() {
    const lettersOnly = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$/;
    const colorRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;

    if (this.vehiculo.anio < 1900 || this.vehiculo.anio > 2100) {
      Swal.fire('Error de Validación', 'El año de fabricación debe estar entre 1900 y 2100.', 'warning');
      return;
    }
    if (this.vehiculo.valor_adquisicion < 0) {
      Swal.fire('Error de Validación', 'El valor de adquisición no puede ser negativo.', 'warning');
      return;
    }
    if (this.vehiculo.marca && !lettersOnly.test(this.vehiculo.marca.trim())) {
      Swal.fire('Error de Validación', 'La marca solo debe contener letras y espacios.', 'warning');
      return;
    }
    if (this.vehiculo.color && !colorRegex.test(this.vehiculo.color.trim())) {
      Swal.fire('Error de Validación', 'El color solo debe contener letras y espacios.', 'warning');
      return;
    }

    this.guardando = true;
    this.vehiculo.nombre = `${this.vehiculo.marca} ${this.vehiculo.modelo} (${this.vehiculo.placa})`;
    this.vehiculo.descripcion = `Automotor de la DEM. Placa: ${this.vehiculo.placa}. Motor: ${this.vehiculo.serial_motor}. Color: ${this.vehiculo.color}.`;

    const request = this.editando
      ? this.inventarioService.updateAutomotor(this.editId!, this.vehiculo)
      : this.inventarioService.createAutomotor(this.vehiculo);

    request.subscribe({
      next: () => {
        Swal.fire({
          title: this.editando ? '¡Automotor Actualizado!' : '¡Vehículo Incorporado!',
          text: this.editando
            ? 'Los datos del automotor han sido actualizados.'
            : 'El automotor ha sido registrado exitosamente en el inventario.',
          icon: 'success',
          confirmButtonColor: '#2c3e50'
        });
        this.router.navigate(['/automotor']);
      },
      error: (err) => {
        console.error('Error:', err);
        const errorMsg = err.error?.anio?.[0] || err.error?.marca?.[0] || err.error?.color?.[0]
          || err.error?.valor_adquisicion?.[0]
          || 'No se pudo guardar el registro del vehículo. Verifique los datos o seriales repetidos.';
        Swal.fire({ title: 'Error', text: errorMsg, icon: 'error', confirmButtonColor: '#2c3e50' });
        this.guardando = false;
      }
    });
  }
}
