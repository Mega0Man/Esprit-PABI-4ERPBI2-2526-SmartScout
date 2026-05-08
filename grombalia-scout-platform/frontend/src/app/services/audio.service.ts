/* src/app/services/audio.service.ts */
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  private synth: SpeechSynthesis = window.speechSynthesis;
  public onEnd$ = new Subject<void>();

  constructor() { }

  /**
   * Lit le texte à voix haute en utilisant window.speechSynthesis.
   * @param text Le texte à lire.
   * @param lang La langue ('fr-FR' ou 'en-US').
   */
  speak(text: string, lang: 'fr-FR' | 'en-US'): void {
    this.stop();

    const utterance = new SpeechSynthesisUtterance(text);
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
