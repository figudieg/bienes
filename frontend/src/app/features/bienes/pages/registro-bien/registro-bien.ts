import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { InventarioService } from '../../../../core/services/inventario.service';
import { PATRON_LETRAS_CON_BARRA, PATRON_CONTIENE_LETRA } from '../../../../shared/utils/validadores-texto.util';
import { mostrarErrorHttp } from '../../../../shared/utils/http-error.util';
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

  categorias = [
    { value: 'COMPUTADORA', label: 'Computadora / Equipo de Computación' },
    { value: 'PANTALLA', label: 'Pantalla / Monitor' },
    { value: 'PERIFERICO', label: 'Periférico (Mouse, Teclado, etc.)' },
    { value: 'MOBILIARIO', label: 'Mobiliario (Escritorio, Silla, Archivador)' },
    { value: 'EQUIPO_OFICINA', label: 'Equipo de Oficina (Impresora, Fotocopiadora)' },
    { value: 'ELECTRODOMESTICO', label: 'Electrodoméstico' },
    { value: 'HERRAMIENTA', label: 'Herramienta / Equipo Técnico' },
    { value: 'OTRO', label: 'Otro' },
  ];

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
      nombre: ['', [Validators.required, Validators.minLength(3), Validators.pattern(PATRON_CONTIENE_LETRA)]],
      descripcion: ['', Validators.required],
      serial_fabrica: [''],
      codigo_inventario: ['', Validators.required],
      estado: ['ACTIVO', Validators.required],
      categoria: ['', Validators.required],
      sede: ['', Validators.required],
      orden_compra: [''],
      fecha_adquisicion: [new Date().toISOString().substring(0, 10), Validators.required],
      valor_adquisicion: [0, [Validators.required, Validators.min(0)]],
      caracteristicas: [''],
      color_mueble: ['', Validators.pattern(PATRON_LETRAS_CON_BARRA)],
      material: ['', Validators.pattern(PATRON_LETRAS_CON_BARRA)],
      componente: [''],
      marca_componente: [''],
      modelo_componente: [''],
      serial_componente: ['']
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
        error: (err) => mostrarErrorHttp(err, { mensajeFallback: 'No se pudo cargar el bien.' })
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
        mostrarErrorHttp(err, {
          mensajeValidacion: () => err.error?.codigo_inventario?.[0] || err.error?.serial_fabrica?.[0],
          mensajeFallback: 'No se pudo guardar el bien. Verifique que el código de inventario o el serial no estén repetidos.'
        });
        this.cargando = false;
      }
    });
  }

  cancelar() { this.router.navigate(['/bienes']); }
}
