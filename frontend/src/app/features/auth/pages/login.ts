import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login {
  credentials = {
    username: '',
    password: ''
  };
  errorMessage: string = '';
  isLoading: boolean = false;

  // Estados de recuperación
  mostrarRecuperarModal = false;
  recuperarPaso = 1;
  cargandoRecuperar = false;
  recoveredUsername = '';
  recuperarForm = {
    username: '',
    code: '',
    newPassword: '',
    confirmPassword: ''
  };

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  async onSubmit() {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      const success = await this.authService.login(
        this.credentials.username,
        this.credentials.password
      );

      if (success) {
        this.router.navigate(['/inicio']);
      } else {
        this.errorMessage = 'Usuario o contraseña incorrectos';
      }
    } catch (error) {
      this.errorMessage = 'Error al conectar con el servidor';
    } finally {
      this.isLoading = false;
    }
  }

  abrirRecuperarModal() {
    this.recuperarForm = {
      username: '',
      code: '',
      newPassword: '',
      confirmPassword: ''
    };
    this.recuperarPaso = 1;
    this.recoveredUsername = '';
    this.mostrarRecuperarModal = true;
  }

  cerrarRecuperarModal() {
    this.mostrarRecuperarModal = false;
  }

  async solicitarCodigo() {
    if (!this.recuperarForm.username) return;
    this.cargandoRecuperar = true;
    try {
      await this.authService.forgotCredentials(this.recuperarForm.username);
      Swal.fire('Solicitud de Código', 'Se ha generado la solicitud de recuperación. Pídale el código de verificación al Administrador.', 'success');
      this.recuperarPaso = 2;
    } catch (error: any) {
      console.error(error);
      const msg = error.error?.error || 'No se pudo generar la solicitud de recuperación.';
      Swal.fire('Error', msg, 'error');
    } finally {
      this.cargandoRecuperar = false;
    }
  }

  async verificarCodigo() {
    if (!this.recuperarForm.username || !this.recuperarForm.code) return;
    this.cargandoRecuperar = true;
    try {
      const res = await this.authService.verifyCode(this.recuperarForm.username, this.recuperarForm.code);
      this.recoveredUsername = res.username;
      Swal.fire('Código Verificado', `Código validado con éxito. Usuario: ${res.username}`, 'success');
      this.recuperarPaso = 3;
    } catch (error: any) {
      console.error(error);
      const msg = error.error?.error || 'Código incorrecto o vencido.';
      Swal.fire('Error', msg, 'error');
    } finally {
      this.cargandoRecuperar = false;
    }
  }

  async restablecerPassword() {
    if (this.recuperarForm.newPassword.length < 8) {
      Swal.fire('Error', 'La contraseña debe tener al menos 8 caracteres.', 'warning');
      return;
    }
    if (this.recuperarForm.newPassword !== this.recuperarForm.confirmPassword) {
      Swal.fire('Error', 'Las contraseñas no coinciden.', 'warning');
      return;
    }
    this.cargandoRecuperar = true;
    try {
      await this.authService.resetCredentials(
        this.recuperarForm.username,
        this.recuperarForm.code,
        this.recuperarForm.newPassword
      );
      Swal.fire('Éxito', 'Contraseña restablecida con éxito. Ya puede iniciar sesión.', 'success');
      this.cerrarRecuperarModal();
    } catch (error: any) {
      console.error(error);
      const msg = error.error?.error || 'Ocurrió un error al restablecer la contraseña.';
      Swal.fire('Error', msg, 'error');
    } finally {
      this.cargandoRecuperar = false;
    }
  }
}