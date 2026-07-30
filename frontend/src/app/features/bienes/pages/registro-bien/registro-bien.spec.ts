import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RegistroBien } from './registro-bien';

describe('RegistroBien', () => {
  let component: RegistroBien;
  let fixture: ComponentFixture<RegistroBien>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegistroBien]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RegistroBien);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
