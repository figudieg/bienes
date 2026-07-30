import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaBienes } from './lista-bienes';

describe('ListaBienes', () => {
  let component: ListaBienes;
  let fixture: ComponentFixture<ListaBienes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaBienes]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListaBienes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
