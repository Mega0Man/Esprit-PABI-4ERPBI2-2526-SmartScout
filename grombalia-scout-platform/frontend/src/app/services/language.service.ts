/* src/app/services/language.service.ts */
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type Lang = 'fr' | 'en';

export interface Translation {
  [key: string]: {
    fr: string;
    en: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private readonly STORAGE_KEY = 'scout_lang';
  private currentLangSubject: BehaviorSubject<Lang>;
  public currentLang$;

  public translations: Translation = {
    // General
    'app_name': { fr: 'GROUPE SCOUT GROMBALIA', en: 'GROMBALIA SCOUT GROUP' },
    'welcome': { fr: 'Bienvenue', en: 'Welcome' },
    'logout': { fr: 'Déconnexion', en: 'Logout' },
    'overview': { fr: 'Vue d\'ensemble', en: 'Overview' },
    'home': { fr: 'Accueil', en: 'Home' },
    
    // Roles
    'group_leader': { fr: 'Chef de Groupe', en: 'Group Leader' },
    'treasurer': { fr: 'Trésorier', en: 'Treasurer' },
    'unit_leader': { fr: 'Chef d\'Unité', en: 'Unit Leader' },
    'dashboard': { fr: 'Tableau de Bord', en: 'Dashboard' },

    // Login/Signup
    'sign_in': { fr: 'Se connecter', en: 'Sign In' },
    'password_tab': { fr: 'Mot de passe', en: 'Password' },
    'face_tab': { fr: 'Face ID', en: 'Face ID' },
    'register_tab': { fr: 'S\'inscrire', en: 'Register' },
    'username': { fr: 'Nom d\'utilisateur', en: 'Username' },
    'password': { fr: 'Mot de passe', en: 'Password' },
    'national_id': { fr: 'CIN (8 chiffres)', en: 'National ID (8 digits)' },
    'enable_face': { fr: 'Activer la reconnaissance faciale pour une connexion rapide', en: 'Enable Face Recognition for Faster Login' },
    'face_hint': { fr: 'Capturez votre visage pour vous connecter instantanément la prochaine fois.', en: 'Capture your face to log in instantly next time.' },
    'complete_reg': { fr: 'Terminer l\'inscription', en: 'Complete Registration' },
    'no_account': { fr: 'Pas encore de compte ?', en: 'Don\'t have an account?' },
    'register_here': { fr: 'Inscrivez-vous ici', en: 'Register here' },

    // Dashboard ML Modules
    'scout_forecast': { fr: 'Prévision des Scouts', en: 'Scout Forecast' },
    'classification': { fr: 'Classification', en: 'Classification' },
    'anomaly_detection': { fr: 'Détection d\'Anomalies', en: 'Anomaly Detection' },
    'recommendation': { fr: 'Système de Recommandation', en: 'Recommendation System' },
    'power_bi_reports': { fr: 'Rapports Power BI', en: 'Power BI Reports' },
    
    // Audio messages
    'audio_welcome_fr': { fr: 'Vous êtes sur la page d\'accueil du tableau de bord', en: 'You are on the overview page of the dashboard' },
    'audio_welcome_en': { fr: 'You are on the overview page of the', en: 'You are on the overview page of the' },
    'audio_dashboard': { fr: 'Tableau de bord', en: 'Dashboard' },

    // Home values
    'adventure': { fr: 'Aventure', en: 'Adventure' },
    'teamwork': { fr: 'Travail d\'équipe', en: 'Teamwork' },
    'values': { fr: 'Valeurs', en: 'Values' },
    'leadership': { fr: 'Leadership', en: 'Leadership' }
  };

  constructor() {
    const savedLang = localStorage.getItem(this.STORAGE_KEY) as Lang;
    const initialLang: Lang = (savedLang === 'fr' || savedLang === 'en') ? savedLang : 'fr';
    
    this.currentLangSubject = new BehaviorSubject<Lang>(initialLang);
    this.currentLang$ = this.currentLangSubject.asObservable();
  }

  setLanguage(lang: Lang): void {
    localStorage.setItem(this.STORAGE_KEY, lang);
    this.currentLangSubject.next(lang);
  }

  translate(key: string): string {
    const lang = this.currentLangSubject.value;
    return this.translations[key] ? this.translations[key][lang] : key;
  }

  getCurrentLang(): Lang {
    return this.currentLangSubject.value;
  }
}
