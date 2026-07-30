import { Routes } from '@angular/router';
import { ListaAutomotoresComponent } from './pages/lista-automotores/lista-automotores';
import { RegistroAutomotorComponent } from './pages/registro-automotor/registro-automotor';

export const AUTOMOTOR_ROUTES: Routes = [
  { path: '', component: ListaAutomotoresComponent },
  { path: 'nuevo', component: RegistroAutomotorComponent },
  { path: 'editar/:id', component: RegistroAutomotorComponent }
];
