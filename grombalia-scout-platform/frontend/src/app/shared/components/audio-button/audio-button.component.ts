/* src/app/shared/components/audio-button/audio-button.component.ts */
import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { AudioService } from '../../../services/audio.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-audio-button',
  template: `
    <button class="audio-btn" 
            [class.active]="active" 
            [class.finished]="finished"
            (click)="toggle()" 
            [attr.aria-label]="(active ? 'Stop: ' : 'Listen: ') + text" 
            [attr.aria-pressed]="active">
      <span class="icon-container">
        <i [class]="active ? 'icon-stop' : (finished ? 'icon-rotate-right' : 'icon-volume')"></i>
      </span>
      <span class="btn-text">
        {{ getButtonLabel() }}
      </span>
    </button>
  `,
  styles: [`
    .audio-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 20px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: rgba(255, 255, 255, 0.1);
      color: white;
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 14px;
      font-weight: 500;
      backdrop-filter: blur(4px);
    }
    .audio-btn:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.4);
    }
    .audio-btn.active {
      background: rgba(231, 76, 60, 0.2);
      border-color: #e74c3c;
      color: #e74c3c;
      box-shadow: 0 0 10px rgba(231, 76, 60, 0.3);
    }
    .audio-btn.finished {
      background: rgba(52, 152, 219, 0.2);
      border-color: #3498db;
      color: #3498db;
    }
    .icon-container {
      display: flex;
      align-items: center;
      font-size: 18px;
    }
    .btn-text {
      white-space: nowrap;
    }
    /* Simple icon fallbacks if icons are missing */
    .icon-stop::before { content: "■"; }
    .icon-volume::before { content: "🔊"; }
    .icon-rotate-right::before { content: "↻"; }
  `]
})
export class AudioButtonComponent implements OnInit, OnDestroy {
  @Input() text!: string;
  @Input() lang!: 'fr' | 'en';

  active = false;
  finished = false;
  private sub: Subscription = new Subscription();

  constructor(private audioService: AudioService) { }

  ngOnInit(): void {
    this.sub.add(
      this.audioService.onEnd$.subscribe(() => {
        this.active = false;
        this.finished = true;
      })
    );
  }

  ngOnDestroy(): void {
    this.audioService.stop();
    this.sub.unsubscribe();
  }

  getButtonLabel(): string {
    if (this.active) {
      return this.lang === 'fr' ? 'Arrêter' : 'Stop';
    }
    if (this.finished) {
      return this.lang === 'fr' ? 'Réécouter' : 'Replay';
    }
    return this.lang === 'fr' ? 'Écouter' : 'Listen';
  }

  toggle(): void {
    if (this.active) {
      this.audioService.stop();
      this.active = false;
    } else {
      this.active = true;
      this.finished = false;
      const fullLang = this.lang === 'fr' ? 'fr-FR' : 'en-US';
      this.audioService.speak(this.text, fullLang);
    }
  }
}
