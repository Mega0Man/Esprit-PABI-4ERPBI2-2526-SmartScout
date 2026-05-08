import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { LanguageService, Lang } from '../services/language.service';
import { AudioService } from '../services/audio.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  currentLang$ = this.languageService.currentLang$;

  constructor(
    private router: Router,
    private languageService: LanguageService,
    private audioService: AudioService
  ) { }

  getTranslation(key: string): string {
    return this.languageService.translate(key);
  }

  setLang(lang: Lang): void {
    this.audioService.stop();
    this.languageService.setLanguage(lang);
  }

  goToLogin(role: string): void {
    this.router.navigate(['/login', role]);
  }
}
