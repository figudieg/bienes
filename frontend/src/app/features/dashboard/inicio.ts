import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';
import { InventarioService } from '../../core/services/inventario.service';

@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './inicio.html',
  styleUrls: ['./inicio.css']
})
export class Inicio implements OnInit {
  rol: string | null = null;
  stats = { totalBienes: 0, bienesActivos: 0, bienesInactivos: 0, bienesDesincorporados: 0 };
  ultimosLogs: any[] = [];

  constructor(
    private authService: AuthService,
    private inventarioService: InventarioService
  ) {}

  ngOnInit() {
    const user = this.authService.getCurrentUser();
    this.rol = user?.rol ?? null;
    this.cargarEstadisticas();
    this.cargarUltimosLogs();
  }

  cargarEstadisticas() {
    this.inventarioService.getBienes().subscribe({
      next: (bienes: any[]) => {
        this.stats.totalBienes = bienes.length;
        this.stats.bienesActivos = bienes.filter(b => b.estado === 'ACTIVO').length;
        this.stats.bienesInactivos = bienes.filter(b => b.estado === 'INACTIVO').length;
        this.stats.bienesDesincorporados = bienes.filter(b => b.estado === 'DESINCORPORADO').length;
      },
      error: (err) => console.error('Error cargando bienes:', err)
    });
  }

  cargarUltimosLogs() {
    this.inventarioService.getLogs().subscribe({
      next: (logs: any[]) => {
        this.ultimosLogs = logs.slice(0, 8);
      },
      error: (err) => console.error('Error cargando logs:', err)
    });
  }
}
