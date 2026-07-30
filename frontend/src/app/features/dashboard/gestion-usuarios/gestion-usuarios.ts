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
  searchQuery = '';
  cargando = true;

  modalAbierto = false;
  editando = false;
  guardando = false;

  form: any = {
    id: null,
    username: '',
    first_name: '',
    last_name: '',
    cedula: '',
    email: '',
    cargo: '',
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
    this.form = { id: null, username: '', first_name: '', last_name: '', cedula: '', email: '', cargo: '', rol: 'OPERADOR', is_active: true, password: '' };
    this.modalAbierto = true;
  }

  abrirEditar(u: any) {
    this.editando = true;
    this.form = { ...u, password: '' };
    this.modalAbierto = true;
  }

  cerrarModal() {
    this.modalAbierto = false;
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
        const msg = err.error?.username?.[0] || err.error?.cedula?.[0] || err.error?.password?.[0] || 'No se pudo guardar el usuario.';
        Swal.fire('Error', msg, 'error');
        this.guardando = false;
      }
    });
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
