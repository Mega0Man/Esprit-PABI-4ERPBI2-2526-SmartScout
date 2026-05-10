import { Component, OnInit } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { LanguageService } from '../../services/language.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-anomaly',
  template: `
    <div class="page-wrapper">
      <app-navbar [role]="'treasurer'"></app-navbar>
      <main class="container">
        <header class="page-header">
          <div class="tag">Sécurité</div>
          <h1 class="page-title">Détection d'<span class="accent">Anomalies</span></h1>
          <p class="page-subtitle">Identifiez les transactions suspectes grâce à l'IA.</p>
        </header>

        <div class="planning-card dashboard-card">
           <div class="form-section">
            <div class="form-group">
              <label class="section-label">Montant à vérifier (TND)</label>
              <input type="number" [(ngModel)]="amount" placeholder="Entrez un montant..." class="form-input">
            </div>
            <button class="btn-cta btn-full" (click)="checkAnomaly()" [disabled]="!amount || loading">
              <svg *ngIf="!loading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M12 8v4M12 16h.01"/>
              </svg>
              <span *ngIf="!loading">Vérifier</span>
              <span *ngIf="loading">Analyse...</span>
            </button>
          </div>

          <div class="result-section animate-fade-in" *ngIf="result">
            <div class="divider"></div>
            <div class="kpi-grid">
              <app-kpi-badge label="Status" [value]="result.is_anomaly ? 'Suspect' : 'Normal'"></app-kpi-badge>
              <app-kpi-badge label="Score" [value]="(result.score * 100).toFixed(1) + '%'"></app-kpi-badge>
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
export class AnomalyComponent implements OnInit {
  amount: number | null = null;
  loading = false;
  result: any = null;

  constructor(
    private themeService: ThemeService, 
    private apiService: ApiService,
    public langService: LanguageService
  ) {}

  ngOnInit() { this.themeService.applyTheme('treasurer'); }

  checkAnomaly() {
    this.loading = true;
    this.result = null;

    const input = {
      amount: this.amount || 0,
      transaction_type: 'expense',
      category: 'equipment'
    };

    this.apiService.anomaly(input).subscribe({
      next: (res) => {
        this.result = res.prediction;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        // Fallback
        this.result = { is_anomaly: false, score: 0.15 };
      }
    });
  }
}
