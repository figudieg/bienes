import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InventarioService } from '../../../../core/services/inventario.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-nueva-asignacion',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './nueva-asignacion.html',
  styleUrls: ['./nueva-asignacion.css']
})
export class NuevaAsignacionComponent implements OnInit {
  form!: FormGroup;
  bienes: any[] = [];
  areas: any[] = [];
  cargando = false;
  buscandoUsuario = false;
  usuarioEncontrado: any = null;
  errorCedula: string = '';

  constructor(
    private fb: FormBuilder,
    private inventarioService: InventarioService,
    private router: Router
  ) {}

  ngOnInit() {
    this.form = this.fb.group({
      bien: ['', Validators.required],
      cedula: ['', [Validators.required, Validators.minLength(6)]],
      usuario: [null, Validators.required],
      area: [null, Validators.required],
    });
    this.inventarioService.getBienes().subscribe({
      next: (d: any[]) => this.bienes = d.filter(b => b.estado === 'ACTIVO'),
      error: () => Swal.fire('Error', 'No se pudieron cargar los bienes. Recargue la página.', 'error')
    });
    this.inventarioService.getAreas().subscribe({
      next: (d: any) => this.areas = Array.isArray(d) ? d : (d.results || []),
      error: () => Swal.fire('Error', 'No se pudieron cargar las áreas. Recargue la página.', 'error')
    });
  }

  buscarUsuario() {
    const cedula = this.form.get('cedula')?.value?.trim();
    if (!cedula || cedula.length < 6) {
      this.errorCedula = 'Ingrese un número de cédula válido (mínimo 6 dígitos).';
      this.usuarioEncontrado = null;
      this.form.patchValue({ usuario: null });
      return;
    }

    this.buscandoUsuario = true;
    this.errorCedula = '';
    this.usuarioEncontrado = null;
    this.form.patchValue({ usuario: null });

    this.inventarioService.buscarUsuarioPorCedula(cedula).subscribe({
      next: (usuario: any) => {
        this.usuarioEncontrado = usuario;
        this.form.patchValue({ usuario: usuario.id });
        this.buscandoUsuario = false;
      },
      error: (err) => {
        this.buscandoUsuario = false;
        if (err.status === 404) {
          this.errorCedula = `No se encontró un usuario con la cédula ${cedula}.`;
        } else {
          this.errorCedula = 'Error al buscar el usuario. Intente nuevamente.';
        }
      }
    });
  }

  limpiarUsuario() {
    this.usuarioEncontrado = null;
    this.form.patchValue({ cedula: '', usuario: null });
    this.errorCedula = '';
  }

  guardar() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.cargando = true;

    const payload = {
      bien: this.form.value.bien,
      usuario: this.form.value.usuario,
      area: this.form.value.area,
    };

    this.inventarioService.createAsignacion(payload).subscribe({
      next: () => {
        Swal.fire('¡Éxito!', 'Asignación registrada correctamente.', 'success');
        this.router.navigate(['/asignaciones']);
      },
      error: (err) => {
        console.error(err);
        const e = err.error;
        const mensaje =
          e?.bien?.[0] ||
          e?.area?.[0] ||
          e?.detail ||
          (typeof e === 'string' ? e : null) ||
          'Ocurrió un error al registrar la asignación.';
        Swal.fire('Error', mensaje, 'error');
        this.cargando = false;
      }
    });
  }

  cancelar() { this.router.navigate(['/asignaciones']); }
}
