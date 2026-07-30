import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NuevaAsignacion } from './nueva-asignacion';

describe('NuevaAsignacion', () => {
  let component: NuevaAsignacion;
  let fixture: ComponentFixture<NuevaAsignacion>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NuevaAsignacion]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NuevaAsignacion);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
