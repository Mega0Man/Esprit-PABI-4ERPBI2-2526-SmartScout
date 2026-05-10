import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-kpi-badge',
  template: `
    <div class="kpi-badge">
      <span class="label">{{ label }}</span>
      <span class="value kpi-value">{{ value }}</span>
    </div>
  `,
  styles: [`
    .kpi-badge {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 16px;
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      transition: transform var(--transition-base);
      
      &:hover {
        transform: translateY(-2px);
      }
    }
    .label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--color-text-secondary);
      font-weight: 700;
    }
    .value {
      font-size: 24px;
      font-weight: 800;
      color: var(--color-accent);
      letter-spacing: -0.02em;
    }
  `]
})
export class KpiBadgeComponent {
  @Input() label: string = '';
  @Input() value: string | number = '';
}
