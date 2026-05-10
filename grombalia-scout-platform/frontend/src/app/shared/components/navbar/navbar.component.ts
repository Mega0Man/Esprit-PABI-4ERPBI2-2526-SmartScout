import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../../services/auth.service';
import { LanguageService, Lang } from '../../../services/language.service';
import { Role } from '../../../core/services/theme.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit, OnDestroy {
  @Input() role: Role = 'none';
  currentUser: { username?: string } | null = null;
  private userSub?: Subscription;

  constructor(
    private authService: AuthService,
    private router: Router,
    public langService: LanguageService
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.userSub = this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  ngOnDestroy(): void {
    this.userSub?.unsubscribe();
  }

  translate(key: string): string {
    return this.langService.translate(key);
  }

  /** Maps navbar role input to translation keys (underscore form). */
  roleTitleKey(): string {
    const map: Record<string, string> = {
      'unit-leader': 'unit_leader',
      'treasurer': 'treasurer',
      'group-leader': 'group_leader'
    };
    return map[this.role] || '';
  }

  /** Logged-in username from AuthService (stored under `user` in localStorage). */
  get displayName(): string {
    const u = this.currentUser?.username?.trim();
    return u || '';
  }

  get avatarLetter(): string {
    return this.displayName ? this.displayName.charAt(0).toUpperCase() : '?';
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/']);
  }

  setLanguage(lang: string) {
    this.langService.setLanguage(lang as Lang);
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
