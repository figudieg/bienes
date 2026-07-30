import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { InventarioService } from '../../../../core/services/inventario.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-registro-bien',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './registro-bien.html',
  styleUrls: ['./registro-bien.css']
})
export class RegistroBienComponent implements OnInit {
  form!: FormGroup;
  sedes: any[] = [];
  ordenes: any[] = [];
  cargando = false;
  modoEdicion = false;
  bienId: number | null = null;

  // Buffer para lectura rápida de códigos de barras (pistola USB)
  barcodeBuffer: string = '';
  lastKeystrokeTime: number = 0;

  @HostListener('window:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    const now = Date.now();
    
    // Ignorar teclas de control no imprimibles
    if (event.key.length > 1 && event.key !== 'Enter') {
      return;
    }

    // Si el intervalo entre pulsaciones de teclas es > 50ms, asumimos tecleo manual y limpiamos buffer
    if (now - this.lastKeystrokeTime > 50 && this.barcodeBuffer.length > 0) {
      this.barcodeBuffer = '';
    }

    this.lastKeystrokeTime = now;

    if (event.key === 'Enter') {
      if (this.barcodeBuffer.length >= 4) {
        event.preventDefault(); // Detener envío involuntario del formulario
        const scannerValue = this.barcodeBuffer.trim();
        this.barcodeBuffer = '';
        
        // Rellenar automáticamente el campo del Código de Inventario
        this.form.patchValue({ codigo_inventario: scannerValue });
        
        Swal.fire({
          title: 'Código Escaneado',
          text: `Código de inventario asignado: ${scannerValue}`,
          icon: 'success',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 2000
        });
      }
    } else {
      this.barcodeBuffer += event.key;
    }
  }

  constructor(
    private fb: FormBuilder,
    private inventarioService: InventarioService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      descripcion: ['', Validators.required],
      serial_fabrica: [''],
      codigo_inventario: ['', Validators.required],
      estado: ['ACTIVO', Validators.required],
      sede: ['', Validators.required],
      orden_compra: ['']
    });

    this.inventarioService.getSedes().subscribe({ 
      next: (d: any[]) => {
        this.sedes = d;
        if (!this.modoEdicion) {
          const sedeCentral = d.find(s => s.nombre && s.nombre.toLowerCase().includes('central'));
          if (sedeCentral) {
            this.form.patchValue({ sede: sedeCentral.id });
          }
        }
      } 
    });
    this.inventarioService.getOrdenes().subscribe({ next: (d: any[]) => this.ordenes = d });

    this.bienId = this.route.snapshot.params['id'] ? +this.route.snapshot.params['id'] : null;
    if (this.bienId) {
      this.modoEdicion = true;
      this.inventarioService.getBien(this.bienId).subscribe({
        next: (bien: any) => this.form.patchValue(bien),
        error: () => Swal.fire('Error', 'No se pudo cargar el bien.', 'error')
      });
    }
  }

  guardar() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.cargando = true;
    const obs = this.modoEdicion && this.bienId
      ? this.inventarioService.updateBien(this.bienId, this.form.value)
      : this.inventarioService.createBien(this.form.value);

    obs.subscribe({
      next: () => {
        Swal.fire('¡Éxito!', this.modoEdicion ? 'Bien actualizado.' : 'Bien registrado correctamente.', 'success');
        this.router.navigate(['/bienes']);
      },
      error: (err) => {
        console.error(err);
        Swal.fire('Error', 'Ocurrió un error al guardar el bien.', 'error');
        this.cargando = false;
      }
    });
  }

  cancelar() { this.router.navigate(['/bienes']); }
}
