import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { ApiService } from '../services/api.service';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  role!: string;
  roleConfig: any;
  currentUser: any;
  forecastingForm!: FormGroup;
  classificationForm!: FormGroup;
  anomalyForm!: FormGroup;
  recommendationForm!: FormGroup;
  forecastingResult: any;
  classificationResult: any;
  anomalyResult: any;
  recommendationResult: any;
  loading: any = {
    forecasting: false,
    classification: false,
    anomaly: false,
    recommendation: false
  };

  roleConfigs = {
    group_leader: {
      name: 'Group Leader',
      color: '#2c7fb8',
      lightColor: '#5aa0e6',
      gradientFrom: '#1a3a52',
      gradientTo: '#0d2840',
      modules: ['Scout Forecasting', 'Classification'],
      powerBIUrl: 'https://app.powerbi.com/reportEmbed?reportId=5f0c1758-2012-40a7-a892-56464db8d0be&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false&chrome=false&language=en-US',
      grafanaUrl: 'http://localhost:3000/d/group-leader-dashboard'
    },
    treasurer: {
      name: 'Treasurer',
      color: '#d4af37',
      lightColor: '#f0d78c',
      gradientFrom: '#524a1a',
      gradientTo: '#40350d',
      modules: ['Anomaly Detection'],
      powerBIUrl: 'https://app.powerbi.com/reportEmbed?reportId=7094a587-edf8-4891-8ae1-53ce6871a076&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false&chrome=false&language=en-US',
      grafanaUrl: 'http://localhost:3000/d/treasurer-dashboard'
    },
    unit_leader: {
      name: 'Unit Leader',
      color: '#2d8c59',
      lightColor: '#5cb885',
      gradientFrom: '#1a523a',
      gradientTo: '#0d4028',
      modules: ['Recommendation System'],
      powerBIUrl: 'https://app.powerbi.com/reportEmbed?reportId=b2aa5284-6c1f-4c5c-8293-17ba828f5148&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false&chrome=false&language=en-US',
      grafanaUrl: 'http://localhost:3000/d/unit-leader-dashboard'
    }
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private authService: AuthService,
    private apiService: ApiService,
    private sanitizer: DomSanitizer
  ) { }

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    if (!this.currentUser) {
      this.router.navigate(['/']);
      return;
    }

    this.route.params.subscribe(params => {
      this.role = params['role'];
      if (this.currentUser.role !== this.role) {
        this.router.navigate([`/dashboard/${this.currentUser.role}`]);
        return;
      }
      this.roleConfig = this.roleConfigs[this.role as keyof typeof this.roleConfigs];
      if (this.roleConfig?.powerBIUrl) {
        this.roleConfig.powerBIUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.roleConfig.powerBIUrl);
      }
    });

    this.forecastingForm = this.fb.group({ months: [12, [Validators.required, Validators.min(1), Validators.max(24)]] });
    this.classificationForm = this.fb.group({ age: [14, Validators.required], gender: ['male', Validators.required], unit: ['cubs', Validators.required], membership_years: [2, Validators.required] });
    this.anomalyForm = this.fb.group({ amount: [100, Validators.required], transaction_type: ['expense', Validators.required], category: ['supplies', Validators.required] });
    this.recommendationForm = this.fb.group({ scout_id: [1, Validators.required], activity_preferences: [''] });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }

  submitForecasting(): void {
    if (this.forecastingForm.invalid) return;
    this.loading.forecasting = true;
    this.apiService.forecasting(this.forecastingForm.value).subscribe({
      next: (res) => { this.forecastingResult = res; this.loading.forecasting = false; },
      error: () => { this.loading.forecasting = false; }
    });
  }

  submitClassification(): void {
    if (this.classificationForm.invalid) return;
    this.loading.classification = true;
    this.apiService.classification(this.classificationForm.value).subscribe({
      next: (res) => { this.classificationResult = res; this.loading.classification = false; },
      error: () => { this.loading.classification = false; }
    });
  }

  submitAnomaly(): void {
    if (this.anomalyForm.invalid) return;
    this.loading.anomaly = true;
    this.apiService.anomaly(this.anomalyForm.value).subscribe({
      next: (res) => { this.anomalyResult = res; this.loading.anomaly = false; },
      error: () => { this.loading.anomaly = false; }
    });
  }

  submitRecommendation(): void {
    if (this.recommendationForm.invalid) return;
    this.loading.recommendation = true;
    const val = this.recommendationForm.value;
    this.apiService.recommendation({ ...val, activity_preferences: val.activity_preferences.split(',').map((s: string) => s.trim()) }).subscribe({
      next: (res) => { this.recommendationResult = res; this.loading.recommendation = false; },
      error: () => { this.loading.recommendation = false; }
    });
  }

  openModel(modelType: string): void {
    const paths: any = {
      forecast: 'http://localhost:5000',
      classification: 'http://localhost:5002',
      anomaly: 'http://localhost:5004',
      recommendation: 'http://localhost:5003'
    };
    window.open(paths[modelType], '_blank');
  }
}
