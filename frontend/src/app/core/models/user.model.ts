export type UserRole = 
  | 'ADMINISTRADOR' 
  | 'AUDITOR' 
  | 'OPERADOR';

export interface User {
  id: number;
  username: string;
  full_name?: string;
  first_name?: string;
  last_name?: string;
  email: string;
  rol: UserRole;
  cedula?: string;
  cargo?: string;
  unidad_pertenencia_id?: number;
  is_active: boolean;
}
