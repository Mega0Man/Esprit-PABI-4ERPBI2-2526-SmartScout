import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { ChatbotService } from './services/chatbot.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {
  title = 'Grombalia Scout Group';

  constructor(private router: Router, private chatbotService: ChatbotService) {}

  ngOnInit() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.urlAfterRedirects;
      this.updateChatbotContext(url);
    });
  }

  private updateChatbotContext(url: string) {
    let page: any = 'home';
    
    // Reset chat if returning to home
    if (url === '/' || url === '/home' || url === '') {
      this.chatbotService.clearChat();
      this.chatbotService.sendBotGreeting('home');
      page = 'home';
    } else if (url.includes('forecast') || url.includes('planning') || url.includes('group_leader')) {
      page = 'planning';
    } else if (url.includes('classification') || url.includes('members') || url.includes('unit_leader')) {
      page = 'members';
    } else if (url.includes('anomaly') || url.includes('finance') || url.includes('treasurer')) {
      page = 'finance';
    } else if (url.includes('recommendation') || url.includes('activities')) {
      page = 'activities';
    }

    const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
    
    this.chatbotService.setContext({
      page,
      user_name: user.username
    });
  }
}
