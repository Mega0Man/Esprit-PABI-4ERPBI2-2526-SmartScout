/* src/app/shared/components/audio-button/audio-button.component.ts */
import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { AudioService } from '../../../services/audio.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-audio-button',
  template: `
    <button class="audio-btn" 
            [class.active]="active" 
            (click)="toggle()" 
            [attr.aria-label]="(active ? 'Stop: ' : 'Listen: ') + text" 
            [attr.aria-pressed]="active">
      <span class="icon-container">
        <i [class]="active ? 'icon-volume-playing' : 'icon-volume'"></i>
      </span>
      <span class="btn-text">
        {{ active 
          ? (lang === 'fr' ? 'Lecture...' : 'Playing...') 
          : (lang === 'fr' ? 'Écouter' : 'Listen') 
        }}
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
      background: rgba(92, 184, 133, 0.2);
      border-color: #5cb885;
      color: #5cb885;
      box-shadow: 0 0 10px rgba(92, 184, 133, 0.3);
    }
    .icon-container {
      display: flex;
      align-items: center;
      font-size: 18px;
    }
    .btn-text {
      white-space: nowrap;
    }
  `]
})
export class AudioButtonComponent implements OnInit, OnDestroy {
  @Input() text!: string;
  @Input() lang!: 'fr' | 'en';

  active = false;
  private sub: Subscription = new Subscription();

  constructor(private audioService: AudioService) { }

  ngOnInit(): void {
    this.sub.add(
      this.audioService.onEnd$.subscribe(() => {
        this.active = false;
      })
    );
  }

  ngOnDestroy(): void {
    this.audioService.stop();
    this.sub.unsubscribe();
  }

  toggle(): void {
    if (this.active) {
      this.audioService.stop();
      this.active = false;
    } else {
      this.active = true;
      const fullLang = this.lang === 'fr' ? 'fr-FR' : 'en-US';
      this.audioService.speak(this.text, fullLang);
    }
  }
}
