import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TravelPlan } from './travel-plan';

describe('TravelPlan', () => {
  let component: TravelPlan;
  let fixture: ComponentFixture<TravelPlan>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TravelPlan]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TravelPlan);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
