/* src/app/shared/components/scout-assistant/scout-assistant.component.ts */
import { Component, OnInit, OnDestroy, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { ChatbotService, ChatMessage } from '../../../services/chatbot.service';
import { AudioService } from '../../../services/audio.service';
import { LanguageService } from '../../../services/language.service';
import { Subscription } from 'rxjs';
import { Router } from '@angular/router';

@Component({
  selector: 'app-scout-assistant',
  templateUrl: './scout-assistant.component.html',
  styleUrls: ['./scout-assistant.component.scss']
})
export class ScoutAssistantComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;
  
  isOpen = false;
  userInput = '';
  messages: ChatMessage[] = [];
  private sub = new Subscription();

  constructor(
    private chatbotService: ChatbotService,
    private audioService: AudioService,
    private langService: LanguageService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.sub.add(
      this.chatbotService.messages$.subscribe(msgs => {
        this.messages = msgs;
        // Voice response disabled as per user request
      })
    );

    this.sub.add(
      this.langService.currentLang$.subscribe(() => {
        this.chatbotService.refreshMessages();
      })
    );

    this.sub.add(
      this.chatbotService.nav$.subscribe(path => {
        setTimeout(() => {
          this.router.navigate([path]);
          this.isOpen = false;
        }, 1500); // Give time for the assistant to finish speaking
      })
    );
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  toggleChat(): void {
    this.isOpen = !this.isOpen;
    if (this.isOpen && this.messages.length === 0) {
      this.chatbotService.getResponse('hello');
    }
  }

  sendMessage(): void {
    if (!this.userInput.trim()) return;
    const query = this.userInput;
    this.userInput = '';
    this.chatbotService.getResponse(query);
  }

  private speakResponse(text: string): void {
    const lang = this.langService.getCurrentLang();
    const locale = lang === 'fr' ? 'fr-FR' : (lang === 'en' ? 'en-US' : 'ar-SA');
    this.audioService.speak(text, locale);
  }

  private scrollToBottom(): void {
    try {
      this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }

  getTranslation(key: string): string {
    return this.langService.translate(key);
  }

  isRtl(): boolean {
    return this.langService.getCurrentLang() === 'ar';
  }

  isLoginPage(): boolean {
    return this.router.url.includes('/login/');
  }

  getThemeColor(): string {
    const url = this.router.url;
    if (url.includes('group_leader')) return '#2c7fb8'; // Blue for Group Leader
    if (url.includes('treasurer')) return '#d4af37';    // Gold/Yellow for Treasurer
    if (url.includes('unit_leader')) return '#DC2626';  // Red for Unit Leader
    return '#EF4444'; // Default accent fallback
  }
}
