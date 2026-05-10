import { Injectable, Renderer2, RendererFactory2 } from '@angular/core';

export type Role = 'unit-leader' | 'treasurer' | 'group-leader' | 'none';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private renderer: Renderer2;
  private currentTheme: Role = 'none';
  private readonly STORAGE_KEY = 'scout_theme';

  constructor(rendererFactory: RendererFactory2) {
    this.renderer = rendererFactory.createRenderer(null, null);
    this.restoreTheme();
  }

  /**
   * Applies the theme based on the user's role.
   * @param role The role of the user (unit-leader, treasurer, group-leader)
   */
  applyTheme(role: Role): void {
    // Remove previous theme class if any
    if (this.currentTheme !== 'none') {
      this.renderer.removeClass(document.body, `theme-${this.currentTheme}`);
    }

    // Add new theme class
    if (role !== 'none') {
      this.renderer.addClass(document.body, `theme-${role}`);
      localStorage.setItem(this.STORAGE_KEY, role);
    } else {
      localStorage.removeItem(this.STORAGE_KEY);
    }

    this.currentTheme = role;
  }

  /**
   * Restores the theme from localStorage on initialization.
   */
  private restoreTheme(): void {
    const savedTheme = localStorage.getItem(this.STORAGE_KEY) as Role;
    if (savedTheme) {
      this.applyTheme(savedTheme);
    }
  }

  /**
   * Gets the current active theme role.
   */
  getTheme(): Role {
    return this.currentTheme;
  }
}
