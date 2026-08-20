import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class InventarioService {
  private apiUrl = `${environment.apiUrl}/inventario`;

  constructor(private http: HttpClient) {}

  // Bienes
  getBienes(): Observable<any> {
    return this.http.get(`${this.apiUrl}/bienes/`);
  }

  getBien(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/bienes/${id}/`);
  }

  createBien(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/bienes/`, data);
  }

  updateBien(id: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/bienes/${id}/`, data);
  }

  deleteBien(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/bienes/${id}/`);
  }

  deleteAsignacion(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/asignaciones/${id}/`);
  }

  // Sedes
  getSedes(): Observable<any> {
    return this.http.get(`${this.apiUrl}/sedes/`);
  }

  createSede(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/sedes/`, data);
  }

  updateSede(id: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/sedes/${id}/`, data);
  }

  deleteSede(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/sedes/${id}/`);
  }

  // Áreas
  getAreas(): Observable<any> {
    return this.http.get(`${this.apiUrl}/areas/`);
  }

  createArea(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/areas/`, data);
  }

  updateArea(id: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/areas/${id}/`, data);
  }

  deleteArea(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/areas/${id}/`);
  }

  // Asignaciones
  getAsignaciones(): Observable<any> {
    return this.http.get(`${this.apiUrl}/asignaciones/`);
  }

  // Ordenes de Compra
  getOrdenes(): Observable<any> {
    return this.http.get(`${this.apiUrl}/ordenes/`);
  }

  createOrdenCompra(data: FormData | any): Observable<any> {
    return this.http.post(`${this.apiUrl}/ordenes/`, data);
  }

  // Reportes PDF
  descargarReporteOrdenPdf(ordenId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/ordenes/${ordenId}/reporte-pdf/`, {
      responseType: 'blob'
    });
  }

  // Asignaciones
  createAsignacion(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/asignaciones/`, data);
  }

  // Buscar usuario por cédula
  buscarUsuarioPorCedula(cedula: string): Observable<any> {
    return this.http.get(`${environment.apiUrl}/users/gestion/buscar-por-cedula/?cedula=${cedula}`);
  }

  // Consultar datos actualizados del funcionario en SISCOM (DEM) y su estado local
  consultarCedulaSiscom(cedula: string): Observable<any> {
    return this.http.get(`${environment.apiUrl}/users/gestion/consultar-cedula/?cedula=${cedula}`);
  }

  // Listar todos los usuarios
  getUsers(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/users/gestion/`);
  }

  // Listar funcionarios (directorio de personas a quienes se les puede asignar bienes)
  getFuncionarios(): Observable<any> {
    return this.http.get(`${this.apiUrl}/funcionarios/`);
  }

  // Perfil de un funcionario: todos los bienes que tiene asignados actualmente
  getFuncionarioPerfil(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/funcionarios/${id}/perfil/`);
  }

  // Busca un funcionario ya registrado localmente por cédula (sin pasar por SISCOM;
  // sirve de respaldo cuando no hay acceso a la red del DEM)
  buscarFuncionarioLocal(cedula: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/funcionarios/buscar-por-cedula/?cedula=${cedula}`);
  }

  // Auditoría / Logs
  getLogs(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/auditoria/logs/`);
  }

  // Automotores
  getAutomotores(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/automotor/`);
  }

  getAutomotor(id: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/automotor/${id}/`);
  }

  createAutomotor(data: any): Observable<any> {
    return this.http.post(`${environment.apiUrl}/automotor/`, data);
  }

  updateAutomotor(id: number, data: any): Observable<any> {
    return this.http.put(`${environment.apiUrl}/automotor/${id}/`, data);
  }

  deleteAutomotor(id: number): Observable<any> {
    return this.http.delete(`${environment.apiUrl}/automotor/${id}/`);
  }

  // Inmuebles
  getInmuebles(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/inmuebles/`);
  }

  getInmueble(id: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/inmuebles/${id}/`);
  }

  createInmueble(data: any): Observable<any> {
    return this.http.post(`${environment.apiUrl}/inmuebles/`, data);
  }

  updateInmueble(id: number, data: any): Observable<any> {
    return this.http.put(`${environment.apiUrl}/inmuebles/${id}/`, data);
  }

  deleteInmueble(id: number): Observable<any> {
    return this.http.delete(`${environment.apiUrl}/inmuebles/${id}/`);
  }

  // Usuarios
  createUser(data: any): Observable<any> {
    return this.http.post(`${environment.apiUrl}/users/gestion/`, data);
  }

  updateUser(id: number, data: any): Observable<any> {
    return this.http.put(`${environment.apiUrl}/users/gestion/${id}/`, data);
  }

  deleteUser(id: number): Observable<any> {
    return this.http.delete(`${environment.apiUrl}/users/gestion/${id}/`);
  }

  // Trazabilidad loglogística
  getTrazas(): Observable<any> {
    return this.http.get(`${this.apiUrl}/trazabilidad/`);
  }

  // Accesos / Seguridad
  getAccesos(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/auditoria/accesos/`);
  }

  // Descarga del Reporte de Auditoría en PDF
  descargarReporteAuditoriaPdf(): Observable<Blob> {
    return this.http.get(`${environment.apiUrl}/auditoria/logs/reporte-pdf/`, {
      responseType: 'blob'
    });
  }

  // Database status fallback indicator
  getDbStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/bienes/db-status/`);
  }

  // Mass operations
  reasignarMasivo(payload: any): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/bienes/reasignar-masivo/`, payload, {
      responseType: 'blob'
    });
  }

  desincorporarMasivo(payload: any): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/bienes/desincorporar-masivo/`, payload, {
      responseType: 'blob'
    });
  }

  mantenimientoMasivo(payload: any): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/bienes/mantenimiento-masivo/`, payload, {
      responseType: 'blob'
    });
  }

  // Sudebin Excel & PDF endpoints
  importarExcel(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/bienes/importar-excel/`, formData);
  }

  getMantenimientos(): Observable<any> {
    return this.http.get(`${this.apiUrl}/mantenimientos/`);
  }

  descargarComprobanteIncorporacionPdf(bienId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/bienes/${bienId}/comprobante-incorporacion-pdf/`, {
      responseType: 'blob'
    });
  }

  descargarComprobanteReasignacionPdf(trazaId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/trazabilidad/${trazaId}/comprobante-reasignacion-pdf/`, {
      responseType: 'blob'
    });
  }

  descargarFichaMantenimientoPdf(mantId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/mantenimientos/${mantId}/reporte-pdf/`, {
      responseType: 'blob'
    });
  }

  descargarInventarioGeneralPdf(filtros: Record<string, string> = {}): Observable<Blob> {
    const params = Object.entries(filtros)
      .filter(([, v]) => !!v)
      .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
      .join('&');
    const query = params ? `?${params}` : '';
    return this.http.get(`${this.apiUrl}/bienes/inventario-general-pdf/${query}`, {
      responseType: 'blob'
    });
  }
}

