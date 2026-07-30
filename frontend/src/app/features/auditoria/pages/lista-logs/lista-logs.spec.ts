import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaLogs } from './lista-logs';

describe('ListaLogs', () => {
  let component: ListaLogs;
  let fixture: ComponentFixture<ListaLogs>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaLogs]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListaLogs);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
