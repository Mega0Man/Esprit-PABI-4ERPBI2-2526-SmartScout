/* src/app/services/language.service.ts */
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type Lang = 'fr' | 'en' | 'ar';

export interface Translation {
  [key: string]: {
    fr: string;
    en: string;
    ar: string;
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
    'app_name': { fr: 'GROUPE SCOUT GROMBALIA', en: 'GROMBALIA SCOUT GROUP', ar: 'فوج الكشافة بقرنبالية' },
    'welcome': { fr: 'Bienvenue', en: 'Welcome', ar: 'مرحباً' },
    'logout': { fr: 'Déconnexion', en: 'Logout', ar: 'تسجيل الخروج' },
    'overview': { fr: 'Vue d\'ensemble', en: 'Overview', ar: 'نظرة عامة' },
    'home': { fr: 'Accueil', en: 'Home', ar: 'الرئيسية' },
    
    // Roles
    'group_leader': { fr: 'Chef de Groupe', en: 'Group Leader', ar: 'قائد الفوج' },
    'treasurer': { fr: 'Trésorier', en: 'Treasurer', ar: 'أمين الصندوق' },
    'unit_leader': { fr: 'Chef d\'Unité', en: 'Unit Leader', ar: 'قائد وحدة' },
    'dashboard': { fr: 'Tableau de Bord', en: 'Dashboard', ar: 'لوحة القيادة' },

    // Login/Signup
    'sign_in': { fr: 'Se connecter', en: 'Sign In', ar: 'تسجيل الدخول' },
    'password_tab': { fr: 'Mot de passe', en: 'Password', ar: 'كلمة المرور' },
    'face_tab': { fr: 'Face ID', en: 'Face ID', ar: 'بصمة الوجه' },
    'register_tab': { fr: 'S\'inscrire', en: 'Register', ar: 'إنشاء حساب' },
    'username': { fr: 'Nom d\'utilisateur', en: 'Username', ar: 'اسم المستخدم' },
    'password': { fr: 'Mot de passe', en: 'Password', ar: 'كلمة المرور' },
    'national_id': { fr: 'CIN (8 chiffres)', en: 'National ID (8 digits)', ar: 'رقم بطاقة التعريف (8 أرقام)' },
    'enable_face': { fr: 'Activer la reconnaissance faciale pour une connexion rapide', en: 'Enable Face Recognition for Faster Login', ar: 'تفعيل التعرف على الوجه لتسجيل دخول أسرع' },
    'face_hint': { fr: 'Capturez votre visage pour vous connecter instantanément la prochaine fois.', en: 'Capture your face to log in instantly next time.', ar: 'التقط صورة لوجهك لتسجيل الدخول الفوري في المرة القادمة.' },
    'complete_reg': { fr: 'Terminer l\'inscription', en: 'Complete Registration', ar: 'إكمال التسجيل' },
    'no_account': { fr: 'Pas encore de compte ?', en: 'Don\'t have an account?', ar: 'ليس لديك حساب؟' },
    'register_here': { fr: 'Inscrivez-vous ici', en: 'Register here', ar: 'سجل هنا' },

    // Dashboard ML Modules
    'scout_forecast': { fr: 'Prévision des Scouts', en: 'Scout Forecast', ar: 'توقعات الكشافة' },
    'classification': { fr: 'Classification', en: 'Classification', ar: 'التصنيف' },
    'anomaly_detection': { fr: 'Détection d\'Anomalies', en: 'Anomaly Detection', ar: 'كشف التجاوزات' },
    'recommendation': { fr: 'Système de Recommandation', en: 'Recommendation System', ar: 'نظام المقترحات' },
    'power_bi_reports': { fr: 'Rapports Power BI', en: 'Power BI Reports', ar: 'تقارير Power BI' },
    
    // Audio messages
    'audio_welcome_fr': { fr: 'Vous êtes sur la page d\'accueil du tableau de bord', en: 'You are on the overview page of the dashboard', ar: 'أنت الآن في صفحة نظرة عامة على لوحة القيادة' },
    'audio_welcome_en': { fr: 'You are on the overview page of the', en: 'You are on the overview page of the', ar: 'أنت الآن في صفحة نظرة عامة' },
    'audio_dashboard': { fr: 'Tableau de bord', en: 'Dashboard', ar: 'لوحة القيادة' },

    // Home values
    'adventure': { fr: 'Aventure', en: 'Adventure', ar: 'مغامرة' },
    'teamwork': { fr: 'Travail d\'équipe', en: 'Teamwork', ar: 'عمل جماعي' },
    'values': { fr: 'Valeurs', en: 'Values', ar: 'قيم' },
    'leadership': { fr: 'Leadership', en: 'Leadership', ar: 'قيادة' },

    // Additional home strings
    'homepage.motto': { fr: 'UNITÉ • SERVICE • FRATERNITÉ', en: 'UNITY • SERVICE • BROTHERHOOD', ar: 'الوحدة • الخدمة • الأخوّة' },
    'choose_dashboard': { fr: 'CHOISISSEZ VOTRE TABLEAU DE BORD', en: 'CHOOSE YOUR DASHBOARD', ar: 'اختر لوحة القيادة الخاصة بك' },
    'select_role': { fr: 'Sélectionnez votre rôle pour accéder à votre espace', en: 'Select your role to access your dashboard', ar: 'اختر صفتك للوصول إلى لوحة التحكم الخاصة بك' },
    'scout_quote': { fr: 'Servir, aider, construire un monde meilleur.', en: 'To serve, to help, to build a better world.', ar: 'الخدمة، المساعدة، وبناء عالم أفضل.' },
    
    // Login strings
    'login_to_dashboard': { fr: 'Connectez-vous pour accéder au tableau de bord', en: 'Sign in to access the dashboard', ar: 'سجل الدخول للوصول إلى لوحة القيادة' },
    'enter_username': { fr: 'Entrez votre nom d\'utilisateur', en: 'Enter your username', ar: 'أدخل اسم المستخدم' },
    'enter_password': { fr: 'Entrez votre mot de passe', en: 'Enter your password', ar: 'أدخل كلمة المرور' },
    'signing_in': { fr: 'Connexion...', en: 'Signing in...', ar: 'جاري الدخول...' },
    'or': { fr: 'OU', en: 'OR', ar: 'أو' },
    'login_face_id': { fr: 'Connexion avec Face ID', en: 'Login with Face ID', ar: 'الدخول باستخدام بصمة الوجه' },
    'demo_creds': { fr: 'Identifiants de démonstration (nom d\'utilisateur / mot de passe)', en: 'Demo credentials (username / password)', ar: 'بيانات تجريبية (اسم المستخدم / كلمة المرور)' },
    'login': { fr: 'Connexion', en: 'Login', ar: 'تسجيل الدخول' },
    'register_new_face': { fr: 'Nouvelle Inscription', en: 'Register New Face', ar: 'تسجيل وجه جديد' },
    'face_login_note': { fr: 'Note : La connexion faciale ne fonctionne que si elle a été activée lors de l\'inscription.', en: 'Note: Face login only works if enabled during registration.', ar: 'ملاحظة: تسجيل الدخول بالوجه يعمل فقط إذا تم تفعيله عند التسجيل.' },
    'enter_id': { fr: 'Entrez votre CIN', en: 'Enter your 8-digit ID', ar: 'أدخل رقم التعريف الخاص بك' },
    'create_password': { fr: 'Créez un mot de passe', en: 'Create a password', ar: 'أنشئ كلمة مرور' },
    'capture_face': { fr: 'Capturez votre visage pour terminer l\'inscription', en: 'Capture your face to complete registration', ar: 'التقط صورة وجهك لإكمال التسجيل' },
    'face_captured_success': { fr: 'Visage capturé avec succès !', en: 'Face captured successfully!', ar: 'تم التقاط صورة الوجه بنجاح!' },
    'logging_in': { fr: 'Connexion en cours...', en: 'Logging you in...', ar: 'جاري تسجيل الدخول...' },
    'creating_account': { fr: 'Création du compte...', en: 'Creating Account...', ar: 'جاري إنشاء الحساب...' },
    'face_skipped': { fr: 'Reconnaissance faciale ignorée. Utilisez votre mot de passe pour vous connecter.', en: 'Face recognition skipped. You\'ll use your password to log in.', ar: 'تم تخطي التعرف على الوجه. استخدم كلمة المرور للدخول.' },
    'account_created_logging': { fr: '✅ Compte créé ! Connexion en cours...', en: '✅ Account created! Logging you in...', ar: '✅ تم إنشاء الحساب! جاري تسجيل الدخول...' },
    'account_created_manual': { fr: '✅ Compte créé ! Veuillez vous connecter manuellement.', en: '✅ Account created! Please log in manually.', ar: '✅ تم إنشاء الحساب! يرجى تسجيل الدخول يدوياً.' },

    // Dashboard strings
    'scout_pilot_space': { fr: 'Bienvenue sur votre espace de pilotage scout.', en: 'Welcome to your scout management space.', ar: 'مرحباً بك في مساحة الإدارة الكشفية الخاصة بك.' },
    'coming_soon': { fr: 'Rapport Power BI bientôt disponible !', en: 'Power BI report coming soon!', ar: 'تقرير Power BI سيتوفر قريباً!' },
    'share_embed': { fr: 'Partagez votre URL d\'intégration quand vous l\'aurez.', en: 'Share your embed URL when you have it.', ar: 'شارك رابط التضمين الخاص بك عند توفره.' }
  };

  constructor() {
    const savedLang = localStorage.getItem(this.STORAGE_KEY) as Lang;
    const initialLang: Lang = (savedLang === 'fr' || savedLang === 'en' || savedLang === 'ar') ? savedLang : 'fr';
    
    this.currentLangSubject = new BehaviorSubject<Lang>(initialLang);
    this.currentLang$ = this.currentLangSubject.asObservable();
    this.updateDocDirection(initialLang);
  }

  setLanguage(lang: Lang): void {
    localStorage.setItem(this.STORAGE_KEY, lang);
    this.currentLangSubject.next(lang);
    this.updateDocDirection(lang);
  }

  private updateDocDirection(lang: Lang): void {
    const dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.dir = dir;
    document.documentElement.lang = lang;
  }

  translate(key: string): string {
    const lang = this.currentLangSubject.value;
    return this.translations[key] ? this.translations[key][lang] : key;
  }

  getCurrentLang(): Lang {
    return this.currentLangSubject.value;
  }
}
