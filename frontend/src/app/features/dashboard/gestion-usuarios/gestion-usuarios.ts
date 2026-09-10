import { Component, OnInit, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { InventarioService } from '../../../core/services/inventario.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-gestion-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './gestion-usuarios.html'
})
export class GestionUsuariosComponent implements OnInit, AfterViewInit {
  usuarios: any[] = [];
  filteredUsuarios: any[] = [];
  areas: any[] = [];
  cargosSugeridos: string[] = [];
  searchQuery = '';
  cargando = true;

  private static readonly PATRON_SOLO_LETRAS = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
  private static readonly PATRON_CARGO = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s.()\-,]+$/;

  modalAbierto = false;
  editando = false;
  guardando = false;
  buscandoSiscom = false;
  errorSiscom = '';
  camposBloqueadosPorSiscom = true;

  form: any = {
    id: null,
    username: '',
    first_name: '',
    last_name: '',
    cedula: '',
    email: '',
    cargo: '',
    unidad_pertenencia: null,
    rol: 'OPERADOR',
    is_active: true,
    password: ''
  };

  roles = ['ADMINISTRADOR', 'AUDITOR', 'OPERADOR'];

  constructor(
    private inventarioService: InventarioService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.searchQuery = '';
    this.cargarUsuarios();
    this.cargarAreas();
  }

  cargarAreas() {
    this.inventarioService.getAreas().subscribe({
      next: (data: any) => {
        const areas = Array.isArray(data) ? data : (data.results ?? []);
        this.areas = areas
          .filter((a: any) => a.activa !== false)
          .sort((a: any, b: any) => a.nombre.localeCompare(b.nombre, 'es'));
      },
      error: () => {
        console.error('Error al cargar áreas');
      }
    });
  }

  private actualizarCargosSugeridos() {
    const cargos = this.usuarios
      .map(u => (u.cargo || '').trim())
      .filter(c => !!c);
    this.cargosSugeridos = Array.from(new Set(cargos)).sort((a, b) => a.localeCompare(b, 'es'));
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.searchQuery = '';
      this.aplicarFiltro();
      this.cdr.detectChanges();
    }, 200);
  }

  cargarUsuarios() {
    this.cargando = true;
    this.inventarioService.getUsers().subscribe({
      next: (data: any) => {
        this.usuarios = Array.isArray(data) ? data : (data.results ?? []);
        this.aplicarFiltro();
        this.actualizarCargosSugeridos();
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.cargando = false;
        this.cdr.detectChanges();
        Swal.fire('Error', 'No se pudieron cargar los usuarios. Recargue la página.', 'error');
      }
    });
  }

  aplicarFiltro() {
    if (!this.searchQuery) {
      this.filteredUsuarios = this.usuarios;
    } else {
      const q = this.searchQuery.toLowerCase();
      this.filteredUsuarios = this.usuarios.filter(u =>
        (u.username && u.username.toLowerCase().includes(q)) ||
        (u.first_name && u.first_name.toLowerCase().includes(q)) ||
        (u.last_name && u.last_name.toLowerCase().includes(q)) ||
        (u.cedula && u.cedula.toLowerCase().includes(q)) ||
        (u.cargo && u.cargo.toLowerCase().includes(q))
      );
    }
  }

  abrirNuevo() {
    this.editando = false;
    this.errorSiscom = '';
    this.camposBloqueadosPorSiscom = true;
    this.form = { id: null, username: '', first_name: '', last_name: '', cedula: '', email: '', cargo: '', unidad_pertenencia: null, rol: 'OPERADOR', is_active: true, password: '' };
    this.modalAbierto = true;
  }

  abrirEditar(u: any) {
    this.editando = true;
    this.errorSiscom = '';
    this.camposBloqueadosPorSiscom = true;
    this.form = { ...u, password: '' };
    this.modalAbierto = true;
  }

  cerrarModal() {
    this.modalAbierto = false;
  }

  buscarPorCedulaSiscom() {
    const cedulaLimpia = (this.form.cedula || '').replace(/[^0-9]/g, '');
    if (!cedulaLimpia) {
      Swal.fire('Cédula requerida', 'Ingrese el número de cédula (solo dígitos) para consultar SISCOM.', 'warning');
      return;
    }

    this.buscandoSiscom = true;
    this.errorSiscom = '';

    this.inventarioService.consultarCedulaSiscom(cedulaLimpia).subscribe({
      next: (data: any) => {
        this.buscandoSiscom = false;
        this.camposBloqueadosPorSiscom = true;
        this.form.first_name = data.nombres || this.form.first_name;
        this.form.last_name = data.apellidos || this.form.last_name;
        this.form.cargo = data.funcionario?.cargo || this.form.cargo;
        if (data.area_id) {
          this.form.unidad_pertenencia = data.area_id;
        }
        this.form.username = this.generarUsername(this.form.last_name, this.form.first_name);
        Swal.fire({
          title: 'Datos encontrados',
          text: 'Se completaron Nombre, Apellido, Cargo, Área y Usuario con los datos de SISCOM.',
          icon: 'success',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 2500
        });
      },
      error: (err: any) => {
        this.buscandoSiscom = false;
        // Respaldo: si SISCOM no responde, desbloqueamos para no dejar
        // trabado el alta de un usuario nuevo por un problema de red.
        this.camposBloqueadosPorSiscom = false;
        if (err.status === 502) {
          this.errorSiscom = 'No se pudo conectar con SISCOM (red del DEM). Complete los datos manualmente.';
        } else if (err.status === 404) {
          this.errorSiscom = err.error?.error || 'No se encontró esa cédula en SISCOM. Complete los datos manualmente.';
        } else {
          this.errorSiscom = 'Error al consultar SISCOM. Complete los datos manualmente.';
        }
      }
    });
  }

  private limpiarTexto(s: string): string {
    return (s || '')
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-zA-Z]/g, '')
      .toLowerCase();
  }

  private generarUsername(apellido: string, nombre: string): string {
    const partesApellido = this.limpiarTexto((apellido || '').split(' ')[0]).slice(0, 4);
    const partesNombre = this.limpiarTexto((nombre || '').split(' ')[0]).slice(0, 4);
    const base = partesApellido + partesNombre;
    if (!base) return this.form.username || '';

    const existentes = new Set(
      this.usuarios
        .filter(u => !this.editando || u.id !== this.form.id)
        .map(u => (u.username || '').toLowerCase())
    );

    let candidato = base;
    let sufijo = 2;
    while (existentes.has(candidato)) {
      candidato = `${base}${sufijo}`;
      sufijo++;
    }
    return candidato;
  }

  guardar() {
    if (!this.form.username || !this.form.cedula || !this.form.rol) {
      Swal.fire('Campos requeridos', 'Username, cédula y rol son obligatorios.', 'warning');
      return;
    }
    if (!this.editando && !this.form.password) {
      Swal.fire('Contraseña requerida', 'Debe establecer una contraseña para el nuevo usuario.', 'warning');
      return;
    }
    if (this.form.password && this.form.password.length > 0) {
      const p = this.form.password;
      const passwordValida = p.length >= 8 && /[A-Za-z]/.test(p) && /\d/.test(p);
      if (!passwordValida) {
        Swal.fire('Contraseña inválida', 'La contraseña debe tener mínimo 8 caracteres, con al menos una letra y un número.', 'warning');
        return;
      }
    }
    if (this.form.first_name && !GestionUsuariosComponent.PATRON_SOLO_LETRAS.test(this.form.first_name.trim())) {
      Swal.fire('Nombre inválido', 'El nombre solo debe contener letras y espacios.', 'warning');
      return;
    }
    if (this.form.last_name && !GestionUsuariosComponent.PATRON_SOLO_LETRAS.test(this.form.last_name.trim())) {
      Swal.fire('Apellido inválido', 'El apellido solo debe contener letras y espacios.', 'warning');
      return;
    }
    if (this.form.cargo && !GestionUsuariosComponent.PATRON_CARGO.test(this.form.cargo.trim())) {
      Swal.fire('Cargo inválido', 'El cargo solo debe contener letras, espacios o signos comunes (. ( ) - ,).', 'warning');
      return;
    }

    this.guardando = true;
    const payload: any = { ...this.form };
    if (!payload.password) delete payload.password;

    const request = this.editando
      ? this.inventarioService.updateUser(this.form.id, payload)
      : this.inventarioService.createUser(payload);

    request.subscribe({
      next: () => {
        Swal.fire('Guardado', this.editando ? 'Usuario actualizado correctamente.' : 'Usuario creado correctamente.', 'success');
        this.cerrarModal();
        this.cargarUsuarios();
        this.guardando = false;
      },
      error: (err: any) => {
        Swal.fire('Error', this.extraerMensajeError(err), 'error');
        this.guardando = false;
      }
    });
  }

  private extraerMensajeError(err: any): string {
    const body = err?.error;
    if (typeof body === 'string') return body;
    if (body?.detail) return body.detail;
    if (Array.isArray(body?.non_field_errors) && body.non_field_errors.length) {
      return body.non_field_errors[0];
    }
    if (body && typeof body === 'object') {
      for (const campo of Object.keys(body)) {
        const valor = body[campo];
        if (Array.isArray(valor) && valor.length) return valor[0];
        if (typeof valor === 'string') return valor;
      }
    }
    return 'No se pudo guardar el usuario.';
  }

  eliminar(u: any) {
    Swal.fire({
      title: '¿Eliminar usuario?',
      text: `Se eliminará el usuario "${u.username}" permanentemente.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then(result => {
      if (result.isConfirmed) {
        this.inventarioService.deleteUser(u.id).subscribe({
          next: () => {
            this.usuarios = this.usuarios.filter(x => x.id !== u.id);
            this.aplicarFiltro();
            Swal.fire('Eliminado', 'El usuario ha sido eliminado.', 'success');
          },
          error: () => Swal.fire('Error', 'No se pudo eliminar el usuario.', 'error')
        });
      }
    });
  }

  getRolBadge(rol: string): string {
    const map: Record<string, string> = { 'ADMINISTRADOR': 'danger', 'AUDITOR': 'warning', 'OPERADOR': 'primary' };
    return map[rol] || 'secondary';
  }
}
