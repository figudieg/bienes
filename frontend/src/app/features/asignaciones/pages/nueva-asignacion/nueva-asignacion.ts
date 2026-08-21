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
      funcionario: [null, Validators.required],
      area: [null, Validators.required],
    });
    this.inventarioService.getBienes().subscribe({
      next: (d: any[]) => this.bienes = d.filter(b => b.estado === 'ACTIVO' && !b.asignacion_activa),
      error: () => Swal.fire('Error', 'No se pudieron cargar los bienes. Recargue la página.', 'error')
    });
    this.inventarioService.getAreas().subscribe({
      next: (d: any) => {
        const areas = Array.isArray(d) ? d : (d.results || []);
        this.areas = areas.filter((a: any) => a.activa !== false);
      },
      error: () => Swal.fire('Error', 'No se pudieron cargar las áreas. Recargue la página.', 'error')
    });
  }

  buscarUsuario() {
    const cedula = this.form.get('cedula')?.value?.trim();
    if (!cedula || cedula.length < 6) {
      this.errorCedula = 'Ingrese un número de cédula válido (mínimo 6 dígitos).';
      this.usuarioEncontrado = null;
      this.form.patchValue({ funcionario: null });
      return;
    }

    this.buscandoUsuario = true;
    this.errorCedula = '';
    this.usuarioEncontrado = null;
    this.form.patchValue({ funcionario: null });

    this.inventarioService.consultarCedulaSiscom(cedula).subscribe({
      next: (data: any) => {
        this.buscandoUsuario = false;
        const f = data.funcionario;
        this.usuarioEncontrado = {
          nombre_completo: f.nombre_completo,
          cedula: f.cedula,
          cargo: f.cargo,
          unidad_pertenencia_nombre: f.dependencia || data.area_nombre || '—',
        };

        this.form.patchValue({ funcionario: data.funcionario_id });
        if (data.area_id && !this.form.get('area')?.value) {
          this.form.patchValue({ area: data.area_id });
        }
      },
      error: (err) => {
        // Si SISCOM no responde (fuera de la red del DEM), se intenta con el
        // directorio local de funcionarios ya conocidos por el sistema.
        this.inventarioService.buscarFuncionarioLocal(cedula).subscribe({
          next: (f: any) => {
            this.buscandoUsuario = false;
            this.usuarioEncontrado = {
              nombre_completo: `${f.nombres} ${f.apellidos}`,
              cedula: f.cedula,
              cargo: f.cargo,
              unidad_pertenencia_nombre: f.area_nombre || '—',
            };
            this.form.patchValue({ funcionario: f.id });
            if (f.area && !this.form.get('area')?.value) {
              this.form.patchValue({ area: f.area });
            }
          },
          error: () => {
            this.buscandoUsuario = false;
            this.usuarioEncontrado = null;
            if (err.status === 502) {
              this.errorCedula = 'No se pudo conectar con el sistema de RRHH (SISCOM) y este funcionario tampoco está registrado localmente.';
            } else {
              this.errorCedula = err.error?.error || `No se encontró un funcionario con la cédula ${cedula}.`;
            }
          }
        });
      }
    });
  }

  limpiarUsuario() {
    this.usuarioEncontrado = null;
    this.form.patchValue({ cedula: '', funcionario: null });
    this.errorCedula = '';
  }

  guardar() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.cargando = true;

    const payload = {
      bien: this.form.value.bien,
      funcionario: this.form.value.funcionario,
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
