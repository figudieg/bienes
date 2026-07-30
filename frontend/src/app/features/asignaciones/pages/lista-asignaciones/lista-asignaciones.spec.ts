import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaAsignaciones } from './lista-asignaciones';

describe('ListaAsignaciones', () => {
  let component: ListaAsignaciones;
  let fixture: ComponentFixture<ListaAsignaciones>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaAsignaciones]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListaAsignaciones);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
