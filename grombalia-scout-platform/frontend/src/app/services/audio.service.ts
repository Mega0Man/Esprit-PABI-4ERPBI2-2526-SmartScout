/* src/app/services/audio.service.ts */
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { PAGE_AUDIO_CONFIG } from '../config/page-audio.config';

export type LangCode = 'fr-FR' | 'en-US' | 'ar-SA';

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  private synth: SpeechSynthesis = window.speechSynthesis;
  private voices: SpeechSynthesisVoice[] = [];
  public onEnd$ = new Subject<void>();

  private intros = {
    fr: ["Vous êtes sur la page ", "Bienvenue sur la page ", "Cette section vous présente "],
    en: ["You are on the ", "Welcome to the ", "This section shows the "],
    ar: ["أنت الآن في صفحة ", "مرحباً بك في ", "هذا القسم يعرض "]
  };

  constructor() {
    this.loadVoices();
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = () => this.loadVoices();
    }
  }

  private loadVoices(): void {
    this.voices = this.synth.getVoices();
    console.log('AudioService: Available voices loaded:', this.voices.length);
  }

  /**
   * Récupère le texte du résumé pour une page donnée avec rotation des intros.
   */
  getAudioText(pageKey: string, lang: 'fr' | 'en' | 'ar'): string {
    const config = PAGE_AUDIO_CONFIG[pageKey];
    if (!config) return '';

    let text = lang === 'fr' ? config.fr : (lang === 'en' ? config.en : config.ar);
    
    // Rotation des intros pour rendre l'assistant moins robotique
    const introList = lang === 'fr' ? this.intros.fr : (lang === 'en' ? this.intros.en : this.intros.ar);
    const randomIntro = introList[Math.floor(Math.random() * introList.length)];
    
    // Si le texte commence par une intro standard (ex: "Vous êtes sur la page"), on la remplace
    const standardIntros = [
      "Vous êtes sur la page ", "Bienvenue sur la page ", "Cette section vous présente ",
      "You are on the ", "Welcome to the ", "This section shows the ",
      "You are on the page ", "Welcome to ", "This section presents ",
      "أنت الآن في صفحة ", "مرحباً بك في ", "هذا القسم يعرض "
    ];

    for (const intro of standardIntros) {
      if (text.startsWith(intro)) {
        text = text.substring(intro.length);
        break;
      }
    }

    // Reconstruction avec l'intro aléatoire
    const finalLines = text.split('.');
    const firstLine = finalLines[0].trim();
    const remainingText = finalLines.slice(1).join('.');

    // On s'assure que la première phrase n'est pas vide
    const result = `${randomIntro}${firstLine}.${remainingText}`;
    
    return this.preprocessText(result);
  }

  /**
   * Prétraitement du texte pour un rendu plus naturel.
   */
  private preprocessText(text: string): string {
    if (!text) return '';

    // 1. Smart Length Control (max 200 chars)
    if (text.length > 200) {
      const trimmed = text.substring(0, 197);
      text = trimmed.substring(0, Math.min(trimmed.length, trimmed.lastIndexOf(' '))) + '...';
    }

    // 2. Add slight pause for realism
    text = text.replace(/\. /g, '.   ');
    text = text.replace(/, /g, ',  ');
    text = text.replace(/! /g, '!   ');
    text = text.replace(/\? /g, '?   ');
    
    return text;
  }

  /**
   * Finds the best voice for a specific language code.
   */
  private getBestVoice(langCode: LangCode): SpeechSynthesisVoice | null {
    if (this.voices.length === 0) {
      this.loadVoices();
    }

    // Priorities for each language
    const preferredNames: string[] = [];
    if (langCode === 'en-US') {
      preferredNames.push('Google US English', 'Microsoft David', 'Microsoft Zira', 'Samantha', 'Alex');
    } else if (langCode === 'fr-FR') {
      preferredNames.push('Google français', 'Microsoft Hortense', 'Microsoft Julie', 'Thomas', 'Audrey');
    } else if (langCode === 'ar-SA') {
      preferredNames.push('Microsoft Hoda', 'Google العربية', 'Maged', 'Laila');
    }

    // 1. Filter by exact language code
    let filtered = this.voices.filter(v => v.lang === langCode);

    // 2. If no exact match, filter by base language (e.g., 'en' for 'en-US')
    if (filtered.length === 0) {
      const baseLang = langCode.split('-')[0];
      filtered = this.voices.filter(v => v.lang.startsWith(baseLang));
      console.warn(`AudioService: No exact match for ${langCode}, falling back to base language ${baseLang}`);
    }

    if (filtered.length === 0) {
      console.error(`AudioService: No voice found for ${langCode}`);
      return null;
    }

    // 3. Prevent wrong accents (CRITICAL: English shouldn't use a French voice)
    if (langCode.startsWith('en')) {
      filtered = filtered.filter(v => !v.name.toLowerCase().includes('french') && !v.lang.startsWith('fr'));
    }

    // 4. Try to find a preferred voice among the filtered ones
    const best = filtered.find(v => preferredNames.some(name => v.name.includes(name))) || filtered[0];
    
    console.log(`AudioService: Selected voice for ${langCode}:`, best.name, `(${best.lang})`);
    return best;
  }

  /**
   * Lit le texte à voix haute en utilisant window.speechSynthesis.
   * @param text Le texte à lire.
   * @param langCode La langue ('fr-FR', 'en-US', or 'ar-SA').
   */
  speak(text: string, langCode: LangCode): void {
    this.stop();

    const utterance = new SpeechSynthesisUtterance(this.preprocessText(text));
    const selectedVoice = this.getBestVoice(langCode);

    if (selectedVoice) {
      utterance.voice = selectedVoice;
      utterance.lang = selectedVoice.lang;
    } else {
      // Fallback if no voice found
      utterance.lang = langCode;
      console.warn(`AudioService: Using default system voice for ${langCode}`);
    }

    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onend = () => this.onEnd$.next();
    utterance.onerror = (err) => {
      console.error('AudioService: SpeechSynthesis error:', err);
      this.onEnd$.next();
    };

    this.synth.speak(utterance);
  }

  /**
   * Test function to speak sample text in all languages.
   */
  testVoices(): void {
    console.log('AudioService: Testing all voices...');
    this.speak("Testing English voice. Hello everyone.", 'en-US');
    setTimeout(() => {
      this.speak("Test de la voix française. Bonjour à tous.", 'fr-FR');
    }, 4000);
    setTimeout(() => {
      this.speak("تجربة الصوت العربي. مرحباً بالجميع.", 'ar-SA');
    }, 8000);
  }

  /**
   * Arrête toute lecture en cours.
   */
  stop(): void {
    if (this.synth.speaking) {
      this.synth.cancel();
    }
  }

  /**
   * Indique si une lecture est en cours.
   */
  isSpeaking(): boolean {
    return this.synth.speaking;
  }
}
