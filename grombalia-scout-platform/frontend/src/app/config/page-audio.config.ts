export interface AudioSummary {
  fr: string;
  en: string;
  ar: string;
}

export interface PageAudioConfig {
  [key: string]: AudioSummary;
}

export const PAGE_AUDIO_CONFIG: PageAudioConfig = {
  'home': {
    fr: "Bienvenue sur la plateforme Scout de Grombalia. Ici, vous pouvez découvrir nos valeurs, notre équipe et nos dernières actualités. Cette section vous présente l'essence de notre mouvement.",
    en: "Welcome to the Grombalia Scout platform. Here, you can discover our values, our team, and our latest news. This section introduces you to the essence of our movement.",
    ar: "مرحباً بكم في منصة كشافة قرنبالية. هنا يمكنك اكتشاف قيمنا وفريقنا وآخر أخبارنا. هذا القسم يعرفك على جوهر حركتنا."
  },
  'login': {
    fr: "Vous êtes sur la page de connexion. Ici, vous pouvez accéder à votre compte sécurisé par mot de passe ou reconnaissance faciale. Cette section vous permet d'entrer dans votre espace personnel.",
    en: "You are on the login page. Here, you can access your secure account via password or face recognition. This section allows you to enter your personal space.",
    ar: "أنت الآن في صفحة تسجيل الدخول. هنا يمكنك الوصول إلى حسابك المؤمن بكلمة المرور أو بصمة الوجه. هذا القسم يسمح لك بالدخول إلى مساحتك الشخصية."
  },
  'register': {
    fr: "Vous êtes sur la page d'inscription. Ici, vous pouvez créer votre compte en remplissant vos informations personnelles. Cette section vous permet de rejoindre officiellement notre plateforme.",
    en: "You are on the registration page. Here, you can create your account by filling in your personal information. This section helps you officially join our platform.",
    ar: "أنت الآن في صفحة التسجيل. هنا يمكنك إنشاء حسابك عن طريق ملء معلوماتك الشخصية. هذا القسم يسمح لك بالانضمام رسمياً إلى منصتنا."
  },
  'unit-overview': {
    fr: "Vous êtes sur la page Vue d'ensemble du Chef d'Unité. Ici, vous pouvez voir un résumé des activités et des membres de votre unité. Cette section vous aide à suivre rapidement l’état général.",
    en: "You are on the Unit Leader Overview page. Here, you can see a summary of activities and members in your unit. This section helps you quickly understand the overall status.",
    ar: "أنت الآن في صفحة نظرة عامة لقائد الوحدة. هنا يمكنك رؤية ملخص للأنشطة والأعضاء في وحدتك. هذا القسم يساعدك على فهم الوضع العام بسرعة."
  },
  'unit-members': {
    fr: "Vous êtes sur la page des Membres. Ici, vous pouvez gérer les informations de chaque scout de votre unité. Cette section facilite le suivi administratif de vos membres.",
    en: "You are on the Members page. Here, you can manage the information for each scout in your unit. This section facilitates the administrative tracking of your members.",
    ar: "أنت الآن في صفحة الأعضاء. هنا يمكنك إدارة معلومات كل كشاف في وحدتك. هذا القسم يسهل المتابعة الإدارية لأعضائك."
  },
  'group-overview': {
    fr: "Vous êtes sur la page de Vue d'ensemble du Chef de Groupe. Ici, vous pouvez superviser toutes les unités et les activités globales. Cette section vous donne une vision macro de votre groupe.",
    en: "You are on the Group Leader Overview page. Here, you can oversee all units and global activities. This section gives you a macro view of your group.",
    ar: "أنت الآن في صفحة نظرة عامة لقائد الفوج. هنا يمكنك الإشراف على جميع الوحدات والأنشطة العامة. هذا القسم يعطيك رؤية شاملة لفوجك."
  },
  'treasurer-overview': {
    fr: "Vous êtes sur la page de Vue d'ensemble du Trésorier. Ici, vous pouvez gérer et suivre toutes les dépenses et les finances. Cette section vous aide à contrôler le budget efficacement.",
    en: "You are on the Treasurer Overview page. Here, you can manage and track all expenses and finances. This section helps you control your budget effectively.",
    ar: "أنت الآن في صفحة نظرة عامة لأمين الصندوق. هنا يمكنك إدارة ومتابعة جميع النفقات والمالية. هذا القسم يساعدك على التحكم في الميزانية بفعالية."
  },
  'treasurer-expenses': {
    fr: "Vous êtes sur la page Dépenses. Ici, vous pouvez gérer et suivre toutes les dépenses. Cette section vous aide à contrôler le budget efficacement.",
    en: "You are on the Expenses page. Here, you can manage and track all expenses. This section helps you control your budget effectively.",
    ar: "أنت الآن في صفحة النفقات. هنا يمكنك إدارة ومتابعة جميع المصاريف. هذا القسم يساعدك على التحكم في الميزانية بفعالية."
  },
  'treasurer-reports': {
    fr: "Vous êtes sur la page des Rapports Financiers. Ici, vous pouvez générer et consulter les bilans de trésorerie. Cette section assure la transparence de la gestion financière.",
    en: "You are on the Financial Reports page. Here, you can generate and view cash flow statements. This section ensures transparency in financial management.",
    ar: "أنت الآن في صفحة التقارير المالية. هنا يمكنك إنشاء والاطلاع على كشوفات التدفق النقدي. هذا القسم يضمن الشفافية في الإدارة المالية."
  }
};
