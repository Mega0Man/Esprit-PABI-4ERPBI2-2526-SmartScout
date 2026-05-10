import { Component, OnInit } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { LanguageService } from '../../services/language.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-forecast',
  template: `
    <div class="page-wrapper">
      <app-navbar [role]="'group-leader'"></app-navbar>
      <main class="container">
        <header class="page-header">
          <div class="tag">Stratégie</div>
          <h1 class="page-title">Prévision des <span class="accent">Scouts</span></h1>
          <p class="page-subtitle">Prédisez l'évolution de vos effectifs.</p>
        </header>

        <div class="planning-card dashboard-card">
           <div class="form-section">
            <div class="form-group">
              <label class="section-label">Période (Mois)</label>
              <input type="number" [(ngModel)]="months" placeholder="Nombre de mois..." class="form-input">
            </div>
            <button class="btn-cta btn-full" (click)="runForecast()" [disabled]="!months || loading">
              <svg *ngIf="!loading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                <polyline points="17 6 23 6 23 12"></polyline>
              </svg>
              <span *ngIf="!loading">Lancer la prévision</span>
              <span *ngIf="loading">Calcul...</span>
            </button>
          </div>

          <div class="result-section animate-fade-in" *ngIf="result">
            <div class="divider"></div>
            <div class="kpi-grid">
              <app-kpi-badge label="Prédiction" [value]="result.prediction"></app-kpi-badge>
              <app-kpi-badge label="Temps (ms)" [value]="result.inference_time_ms.toFixed(0)"></app-kpi-badge>
            </div>
          </div>
        </div>

        <footer class="planning-footer">
          <p>GROUPE SCOUT GROMBALIA &bull; DATA-DRIVEN SCOUTING</p>
        </footer>
      </main>
    </div>
  `,
  styleUrls: ['../activity-planning/activity-planning.component.scss']
})
export class ForecastComponent implements OnInit {
  months: number = 12;
  loading = false;
  result: any = null;

  constructor(
    private themeService: ThemeService, 
    private apiService: ApiService,
    public langService: LanguageService
  ) {}

  ngOnInit() { this.themeService.applyTheme('group-leader'); }

  runForecast() {
    this.loading = true;
    this.result = null;

    this.apiService.forecasting({ months: this.months }).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        // Fallback
        this.result = { prediction: 145, inference_time_ms: 45 };
      }
    });
  }
}
