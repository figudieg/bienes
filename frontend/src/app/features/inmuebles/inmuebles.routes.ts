import { Routes } from '@angular/router';
import { ListaInmueblesComponent } from './pages/lista-inmuebles/lista-inmuebles';
import { RegistroInmuebleComponent } from './pages/registro-inmueble/registro-inmueble';

export const INMUEBLES_ROUTES: Routes = [
  { path: '', component: ListaInmueblesComponent },
  { path: 'nuevo', component: RegistroInmuebleComponent },
  { path: 'editar/:id', component: RegistroInmuebleComponent }
];
