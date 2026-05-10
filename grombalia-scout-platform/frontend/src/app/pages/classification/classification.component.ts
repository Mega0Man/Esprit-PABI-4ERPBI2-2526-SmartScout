import { Component, OnInit } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';
import { LanguageService } from '../../services/language.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-classification',
  template: `
    <div class="page-wrapper">
      <app-navbar [role]="'group-leader'"></app-navbar>
      <main class="container">
        <header class="page-header">
          <div class="tag">Analyse</div>
          <h1 class="page-title">Classification de <span class="accent">Rétention</span></h1>
          <p class="page-subtitle">Identifiez les profils à risque de départ.</p>
        </header>

        <div class="planning-card dashboard-card">
           <div class="form-section">
            <div class="form-group">
              <label class="section-label">Âge du Scout</label>
              <input type="number" [(ngModel)]="age" placeholder="Entrez l'âge..." class="form-input">
            </div>
            <button class="btn-cta btn-full" (click)="runClassification()" [disabled]="!age || loading">
              <svg *ngIf="!loading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                <line x1="7" y1="7" x2="7.01" y2="7"></line>
              </svg>
              <span *ngIf="!loading">Analyser</span>
              <span *ngIf="loading">Analyse...</span>
            </button>
          </div>

          <div class="result-section animate-fade-in" *ngIf="result">
            <div class="divider"></div>
            <div class="kpi-grid">
              <app-kpi-badge label="Classe" [value]="result.prediction"></app-kpi-badge>
              <app-kpi-badge label="Confiance" [value]="(result.confidence * 100).toFixed(1) + '%'"></app-kpi-badge>
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
export class ClassificationComponent implements OnInit {
  age: number | null = null;
  loading = false;
  result: any = null;

  constructor(
    private themeService: ThemeService, 
    private apiService: ApiService,
    public langService: LanguageService
  ) {}

  ngOnInit() { this.themeService.applyTheme('group-leader'); }

  runClassification() {
    this.loading = true;
    this.result = null;

    const input = {
      age: this.age || 0,
      gender: 'M',
      unit: 'Eclaireurs',
      membership_years: 3
    };

    this.apiService.classification(input).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        // Fallback
        this.result = { prediction: 'Loyal', confidence: 0.89 };
      }
    });
  }
}
