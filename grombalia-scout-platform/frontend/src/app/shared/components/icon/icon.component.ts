import { Component, Input, OnInit } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ICONS } from '../../icons';

@Component({
  selector: 'app-icon',
  template: `<span [innerHTML]="safeSvg" class="app-icon"></span>`,
  styles: [`
    .app-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 1em;
      height: 1em;
    }
    :host ::ng-deep svg {
      width: 100%;
      height: 100%;
    }
  `]
})
export class IconComponent implements OnInit {
  @Input() name: keyof typeof ICONS = 'FLEUR_DE_LIS';
  safeSvg: SafeHtml | null = null;

  constructor(private sanitizer: DomSanitizer) {}

  ngOnInit() {
    this.safeSvg = this.sanitizer.bypassSecurityTrustHtml(ICONS[this.name]);
  }
}
