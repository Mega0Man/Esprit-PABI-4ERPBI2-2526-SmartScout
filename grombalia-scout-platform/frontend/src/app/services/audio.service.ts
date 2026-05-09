/* src/app/services/audio.service.ts */
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { PAGE_AUDIO_CONFIG } from '../config/page-audio.config';

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  private synth: SpeechSynthesis = window.speechSynthesis;
  public onEnd$ = new Subject<void>();

  private intros = {
    fr: ["Vous êtes sur la page ", "Bienvenue sur la page ", "Cette section vous présente "],
    en: ["You are on the ", "Welcome to the ", "This section shows the "]
  };

  constructor() { }

  /**
   * Récupère le texte du résumé pour une page donnée avec rotation des intros.
   */
  getAudioText(pageKey: string, lang: 'fr' | 'en'): string {
    const config = PAGE_AUDIO_CONFIG[pageKey];
    if (!config) return '';

    let text = lang === 'fr' ? config.fr : config.en;
    
    // Rotation des intros pour rendre l'assistant moins robotique
    const introList = lang === 'fr' ? this.intros.fr : this.intros.en;
    const randomIntro = introList[Math.floor(Math.random() * introList.length)];
    
    // Si le texte commence par une intro standard (ex: "Vous êtes sur la page"), on la remplace
    const standardIntros = [
      "Vous êtes sur la page ", "Bienvenue sur la page ", "Cette section vous présente ",
      "You are on the ", "Welcome to the ", "This section shows the ",
      "You are on the page ", "Welcome to ", "This section presents "
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
      text = text.substring(0, 197) + '...';
    }

    // 2. Add slight pause for realism
    // On remplace le point par un point suivi d'un espace plus long
    text = text.replace(/\. /g, '.   ');
    text = text.replace(/, /g, ',  ');
    text = text.replace(/! /g, '!   ');
    text = text.replace(/\? /g, '?   ');
    
    return text;
  }

  /**
   * Lit le texte à voix haute en utilisant window.speechSynthesis.
   * @param text Le texte à lire.
   * @param lang La langue ('fr-FR' ou 'en-US').
   */
  speak(text: string, lang: 'fr-FR' | 'en-US'): void {
    // 4. Auto-stop previous audio
    this.stop();

    const processedText = this.preprocessText(text);
    const utterance = new SpeechSynthesisUtterance(processedText);
    utterance.lang = lang;
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    // Sélection de la voix
    const voices = this.synth.getVoices();
    const preferredVoice = voices.find(v => v.lang === lang) || voices.find(v => v.lang.startsWith(lang.split('-')[0]));
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onend = () => {
      this.onEnd$.next();
    };

    utterance.onerror = (err) => {
      console.error('SpeechSynthesis error:', err);
      this.onEnd$.next();
    };

    this.synth.speak(utterance);
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
