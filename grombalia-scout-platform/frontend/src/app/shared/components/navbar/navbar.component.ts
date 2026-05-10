import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { LanguageService } from '../../../services/language.service';
import { ThemeService, Role } from '../../../core/services/theme.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  @Input() role: Role = 'none';
  currentUser: any;

  constructor(
    private authService: AuthService,
    private router: Router,
    public langService: LanguageService
  ) {
    this.currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/']);
  }

  setLanguage(lang: string) {
    this.langService.setLanguage(lang as any);
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
