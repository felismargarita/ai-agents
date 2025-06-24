import { Component, inject, ViewEncapsulation } from '@angular/core';
import { FormGroup, FormControl, ReactiveFormsModule, FormBuilder} from '@angular/forms';
import {Validators} from '@angular/forms';
import { HttpClient } from '@angular/common/http'
@Component({
  selector: 'app-travel-plan',
  imports: [ReactiveFormsModule],
  templateUrl: './travel-plan.html',
  styleUrl: './travel-plan.scss',
})
export class TravelPlan {
  private formBuilder = inject(FormBuilder);
  private http = inject(HttpClient);
  inprocess = false
  success = false
  planDetail: { reason?: string, vehicle?: string, steps?: string[] } = {
    reason: '',
    vehicle: '',
    steps: []
  }


  planForm = this.formBuilder.group({
    start: ['', Validators.required],
    destination: ['', Validators.required],
    gender: ['', Validators.compose([Validators.required, Validators.pattern(/男|女/)])],
    age: ['', Validators.required]
  })

  

  plan() {
    if(!this.planForm.valid) return
    this.inprocess = true
    this.http.post('http://localhost:8000/plan', this.planForm.value).subscribe(config => {
      this.planDetail = config
      this.inprocess = false
      this.success = true
    })
  }
}
