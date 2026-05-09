/* src/app/services/chatbot.service.ts */
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { LanguageService, Lang } from './language.service';

export interface ChatContext {
  page: 'planning' | 'members' | 'finance' | 'activities' | 'home';
  data?: any;
  user_name?: string;
}

export interface ChatMessage {
  role: 'assistant' | 'user';
  content: {
    answer: string;
    explanation: string;
    action: string;
  };
  voiceText: string;
  timestamp: Date;
}

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {
  private context: ChatContext = { page: 'home' };
  private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  public messages$ = this.messagesSubject.asObservable();
  
  private navSubject = new Subject<string>();
  public nav$ = this.navSubject.asObservable();

  constructor(private langService: LanguageService) {}

  setContext(context: ChatContext) {
    this.context = context;
  }

  private getLang(): Lang {
    return this.langService.getCurrentLang();
  }

  async getResponse(userQuery: string): Promise<void> {
    const lang = this.getLang();
    const page = this.context.page;
    const userName = this.context.user_name;

    // Add user message
    this.addMessage('user', { answer: userQuery, explanation: '', action: '' }, userQuery);

    // Generate smart response based on context
    const response = this.generateContextualResponse(userQuery, page, lang, userName);
    
    // Simulate thinking delay
    setTimeout(() => {
      this.addMessage('assistant', response.content, response.voiceText);
    }, 400);
  }

  async sendBotGreeting(page: 'home' | 'planning' | 'members' | 'finance' | 'activities') {
    const lang = this.getLang();
    const response = this.getModuleResponse(page as any, lang);
    this.addMessage('assistant', response.content, response.voiceText);
  }

  private addMessage(role: 'assistant' | 'user', content: any, voiceText: string) {
    const current = this.messagesSubject.value;
    const newMessage: ChatMessage = {
      role,
      content,
      voiceText,
      timestamp: new Date()
    };
    this.messagesSubject.next([...current, newMessage]);
  }

  private generateContextualResponse(query: string, page: string, lang: Lang, name?: string) {
    const q = query.toLowerCase().trim();
    
    // 1. Number-based Navigation Selection
    if (q === '1' || q.includes('one')) {
      this.navSubject.next('/login/group_leader');
      return this.getModuleResponse('nav_group', lang);
    }
    if (q === '2' || q.includes('two')) {
      this.navSubject.next('/login/treasurer');
      return this.getModuleResponse('nav_treasurer', lang);
    }
    if (q === '3' || q.includes('three')) {
      this.navSubject.next('/login/unit_leader');
      return this.getModuleResponse('nav_unit', lang);
    }

    // 2. Navigation Intent: Login
    if (q.includes('login') || q.includes('sign in') || q.includes('connexion') || q.includes('تسجيل الدخول') || q.includes('go to')) {
      if (q.includes('group') || q.includes('fauj') || q.includes('فوج')) {
        this.navSubject.next('/login/group_leader');
        return this.getModuleResponse('nav_group', lang);
      }
      if (q.includes('treasurer') || q.includes('amin') || q.includes('money') || q.includes('أمين') || q.includes('صندوق')) {
        this.navSubject.next('/login/treasurer');
        return this.getModuleResponse('nav_treasurer', lang);
      }
      if (q.includes('unit') || q.includes('wahda') || q.includes('وحدة')) {
        this.navSubject.next('/login/unit_leader');
        return this.getModuleResponse('nav_unit', lang);
      }
      // Ask which role if not specified
      return this.getModuleResponse('nav_ask_role', lang);
    }

    // 2. Direct Role Mention (without "login")
    if (q.includes('group leader') || q.includes('chef de groupe') || q.includes('قائد فوج')) {
      this.navSubject.next('/login/group_leader');
      return this.getModuleResponse('nav_group', lang);
    }
    if (q.includes('treasurer') || q.includes('trésorier') || q.includes('أمين صندوق')) {
      this.navSubject.next('/login/treasurer');
      return this.getModuleResponse('nav_treasurer', lang);
    }
    if (q.includes('unit leader') || q.includes('chef d\'unité') || q.includes('قائد وحدة')) {
      this.navSubject.next('/login/unit_leader');
      return this.getModuleResponse('nav_unit', lang);
    }

    // 3. Check for specific keywords across all pages
    if (q.includes('members') || q.includes('spirit') || q.includes('scouts')) {
      return this.getModuleResponse('members', lang);
    }
    if (q.includes('money') || q.includes('budget') || q.includes('finance') || q.includes('spend')) {
      return this.getModuleResponse('finance', lang);
    }
    if (q.includes('plan') || q.includes('food') || q.includes('quantity') || q.includes('prepare')) {
      return this.getModuleResponse('planning', lang);
    }
    if (q.includes('activity') || q.includes('game') || q.includes('fun') || q.includes('do next')) {
      return this.getModuleResponse('activities', lang);
    }

    // 2. If no keyword, but it's a greeting
    if (q.includes('hello') || q.includes('hi') || q.includes('hey') || q.includes('bonjour') || q.includes('مرحبا')) {
      return this.getModuleResponse('home', lang, name);
    }

    // 3. Fallback to page-specific help
    return this.getModuleResponse(page as any, lang, name);
  }

  private getModuleResponse(page: 'planning' | 'members' | 'finance' | 'activities' | 'home' | 'nav_group' | 'nav_treasurer' | 'nav_unit' | 'nav_ask_role', lang: Lang, name?: string) {
    const templates: any = {
      nav_ask_role: {
        en: {
          answer: "Which role do you have?",
          explanation: "I can take you to the correct login page. Choose your role by typing its number:",
          action: "1. Group Leader (Planning & Forecast)\n2. Treasurer (Budget & Finance)\n3. Unit Leader (Activities & Members)",
          voice: ""
        },
        fr: {
          answer: "Quel est votre rôle ?",
          explanation: "Je peux vous emmener à la bonne page de connexion. Choisissez votre rôle en tapant son numéro :",
          action: "1. Chef de Groupe (Planification & Prévisions)\n2. Trésorier (Budget & Finances)\n3. Chef d'Unité (Activités & Membres)",
          voice: ""
        },
        ar: {
          answer: "ما هي صفتك الكشفية؟",
          explanation: "يمكنني توجيهك إلى صفحة تسجيل الدخول الصحيحة. اختر صفتك عن طريق كتابة رقمها:",
          action: "1. قائد فوج (التخطيط والتوقعات)\n2. أمين صندوق (الميزانية والمالية)\n3. قائد وحدة (الأنشطة والأعضاء)",
          voice: ""
        }
      },
      nav_group: {
        en: {
          answer: "Taking you to the Group Leader login!",
          explanation: "Redirecting you now...",
          action: "Please wait a moment.",
          voice: "Sure, taking you to the Group Leader login page now."
        },
        fr: {
          answer: "Je vous emmène à la connexion Chef de Groupe !",
          explanation: "Redirection en cours...",
          action: "Veuillez patienter un instant.",
          voice: "Bien sûr, je vous emmène à la page de connexion Chef de Groupe."
        },
        ar: {
          answer: "سأوجهك الآن لتسجيل دخول قائد الفوج!",
          explanation: "جاري التحويل...",
          action: "يرجى الانتظار لحظة.",
          voice: "بالتأكيد، سأوجهك الآن لصفحة تسجيل دخول قائد الفوج."
        }
      },
      nav_treasurer: {
        en: {
          answer: "Taking you to the Treasurer login!",
          explanation: "Redirecting you now...",
          action: "Please wait a moment.",
          voice: "Sure, taking you to the Treasurer login page now."
        },
        fr: {
          answer: "Je vous emmène à la connexion Trésorier !",
          explanation: "Redirection en cours...",
          action: "Veuillez patienter un instant.",
          voice: "Bien sûr, je vous emmène à la page de connexion Trésorier."
        },
        ar: {
          answer: "سأوجهك الآن لتسجيل دخول أمين الصندوق!",
          explanation: "جاري التحويل...",
          action: "يرجى الانتظار لحظة.",
          voice: "بالتأكيد، سأوجهك الآن لصفحة تسجيل دخول أمين الصندوق."
        }
      },
      nav_unit: {
        en: {
          answer: "Taking you to the Unit Leader login!",
          explanation: "Redirecting you now...",
          action: "Please wait a moment.",
          voice: "Sure, taking you to the Unit Leader login page now."
        },
        fr: {
          answer: "Je vous emmène à la connexion Chef d'Unité !",
          explanation: "Redirection en cours...",
          action: "Veuillez patienter un instant.",
          voice: "Bien sûr, je vous emmène à la page de connexion Chef d'Unité."
        },
        ar: {
          answer: "سأوجهك الآن لتسجيل دخول قائد الوحدة!",
          explanation: "جاري التحويل...",
          action: "يرجى الانتظار لحظة.",
          voice: "بالتأكيد، سأوجهك الآن لصفحة تسجيل دخول قائد الوحدة."
        }
      },
      planning: {
        en: {
          answer: "I can help you plan your logistics.",
          explanation: "Based on the expected number of scouts, we can estimate food and equipment needs.",
          action: "Tell me how many scouts you expect, and I'll give you a list.",
          voice: "I can help you with logistics. Tell me the number of scouts, and I'll prepare a plan for you."
        },
        fr: {
          answer: "Je peux vous aider pour la logistique.",
          explanation: "En fonction du nombre de scouts attendus, nous estimons les besoins en nourriture.",
          action: "Dites-moi combien de scouts vous attendez pour recevoir une liste.",
          voice: "Je peux vous aider pour la logistique. Donnez-moi le nombre de scouts attendus."
        },
        ar: {
          answer: "يمكنني مساعدتك في التخطيط اللوجستي.",
          explanation: "بناءً على عدد الكشافة المتوقع، يمكننا تقدير احتياجات الطعام والمعدات.",
          action: "أخبرني بعدد الكشافة المتوقع وسأعطيك قائمة بالاحتياجات.",
          voice: "يمكنني مساعدتك في الأمور اللوجستية. أخبرني بعدد الكشافة وسأقوم بتجهيز خطة لك."
        }
      },
      members: {
        en: {
          answer: "Let's focus on unit morale.",
          explanation: "Keeping scouts engaged is about building strong relationships and fun activities.",
          action: "Try a team-building game or a short feedback circle this week.",
          voice: "Let's boost unit morale. I suggest a team building game or a feedback circle this week."
        },
        fr: {
          answer: "Concentrons-nous sur le moral de l'unité.",
          explanation: "L'engagement des scouts passe par des relations fortes et des activités ludiques.",
          action: "Essayez un jeu de cohésion ou un cercle de parole cette semaine.",
          voice: "Améliorons le moral de l'unité. Je suggère un jeu d'équipe ou un cercle de parole."
        },
        ar: {
          answer: "لنركز على الروح المعنوية للوحدة.",
          explanation: "الحفاظ على تفاعل الكشافة يعتمد على بناء علاقات قوية وأنشطة ممتعة.",
          action: "جرب لعبة بناء فريق أو حلقة نقاش قصيرة هذا الأسبوع.",
          voice: "لنرفع الروح المعنوية. أقترح القيام بلعبة بناء فريق أو حلقة نقاش هذا الأسبوع."
        }
      },
      finance: {
        en: {
          answer: "I'll help you monitor the budget.",
          explanation: "I check for unusual spending to keep our scout funds safe and organized.",
          action: "Double-check any red alerts with your receipts to ensure accuracy.",
          voice: "I'm monitoring the budget. Please check any red alerts with your receipts."
        },
        fr: {
          answer: "Je vous aide à surveiller le budget.",
          explanation: "Je vérifie les dépenses inhabituelles pour protéger nos fonds scouts.",
          action: "Vérifiez les alertes rouges avec vos reçus pour confirmer les montants.",
          voice: "Je surveille le budget. Pensez à vérifier les alertes avec vos reçus."
        },
        ar: {
          answer: "سأساعدك في مراقبة الميزانية.",
          explanation: "أتحقق من أي إنفاق غير عادي للحفاظ على أموال الكشافة آمنة ومنظمة.",
          action: "راجع أي تنبيهات حمراء مع الإيصالات لضمان الدقة.",
          voice: "أنا أراقب الميزانية. يرجى مراجعة التنبيهات مع الإيصالات الخاصة بك."
        }
      },
      activities: {
        en: {
          answer: "Ready for a new adventure?",
          explanation: "I suggest activities that match what your scouts enjoy most.",
          action: "Pick an activity from the suggestions and try it in the next meeting!",
          voice: "Ready for adventure? Try one of my activity suggestions in your next meeting."
        },
        fr: {
          answer: "Prêt pour une nouvelle aventure ?",
          explanation: "Je suggère des activités qui correspondent aux goûts de vos scouts.",
          action: "Choisissez une activité suggérée pour votre prochaine réunion !",
          voice: "Prêt pour l'aventure ? Essayez une de mes suggestions lors de votre prochaine réunion."
        },
        ar: {
          answer: "هل أنت مستعد لمغامرة جديدة؟",
          explanation: "أقترح أنشطة تتناسب مع ما يحبه الكشافة أكثر.",
          action: "اختر نشاطاً من المقترحات وجربه في الاجتماع القادم!",
          voice: "هل أنت مستعد للمغامرة؟ جرب أحد مقترحاتي في اجتماعك القادم."
        }
      },
      home: {
        en: {
          answer: "Where do you want to go now?",
          explanation: "I can take you to the correct login page. Choose your role by typing its number:",
          action: "1. Group Leader (Planning & Forecast)\n2. Treasurer (Budget & Finance)\n3. Unit Leader (Activities & Members)",
          voice: ""
        },
        fr: {
          answer: "Où souhaitez-vous aller maintenant ?",
          explanation: "Je peux vous emmener à la bonne page de connexion. Choisissez votre rôle en tapant son numéro :",
          action: "1. Chef de Groupe (Planification & Prévisions)\n2. Trésorier (Budget & Finances)\n3. Chef d'Unité (Activités & Membres)",
          voice: ""
        },
        ar: {
          answer: "إلى أين تريد الذهاب الآن؟",
          explanation: "يمكنني توجيهك إلى صفحة تسجيل الدخول الصحيحة. اختر صفتك عن طريق كتابة رقمها:",
          action: "1. قائد فوج (التخطيط والتوقعات)\n2. أمين صندوق (الميزانية والمالية)\n3. قائد وحدة (الأنشطة والأعضاء)",
          voice: ""
        }
      }
    };

    const content = templates[page][lang];
    return {
      content: {
        answer: content.answer,
        explanation: content.explanation,
        action: content.action
      },
      voiceText: content.voice
    };
  }

  clearChat() {
    this.messagesSubject.next([]);
  }
}
