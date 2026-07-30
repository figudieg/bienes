import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-bandeja-recuperacion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './bandeja-recuperacion.html',
  styleUrls: ['./bandeja-recuperacion.css']
})
export class BandejaRecuperacionComponent implements OnInit {
  solicitudes: any[] = [];
  cargando = false;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.cargarSolicitudes();
  }

  cargarSolicitudes(): void {
    this.cargando = true;
    this.authService.getRecoveryRequests().subscribe({
      next: (data) => {
        this.solicitudes = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error(err);
        Swal.fire('Error', 'No se pudieron cargar las solicitudes de recuperación.', 'error');
        this.cargando = false;
      }
    });
  }

  copiarCodigo(codigo: string): void {
    navigator.clipboard.writeText(codigo).then(() => {
      Swal.fire({
        title: '¡Código Copiado!',
        text: `El código ${codigo} ha sido copiado al portapapeles.`,
        icon: 'success',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1500
      });
    });
  }
}
