/* src/app/shared/shared.module.ts */
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AudioButtonComponent } from './components/audio-button/audio-button.component';
import { ScoutAssistantComponent } from './components/scout-assistant/scout-assistant.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { IconComponent } from './components/icon/icon.component';
import { KpiBadgeComponent } from './components/kpi-badge/kpi-badge.component';

@NgModule({
  declarations: [
    AudioButtonComponent,
    ScoutAssistantComponent,
    NavbarComponent,
    IconComponent,
    KpiBadgeComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    RouterModule
  ],
  exports: [
    CommonModule,
    FormsModule,
    RouterModule,
    AudioButtonComponent,
    ScoutAssistantComponent,
    NavbarComponent,
    IconComponent,
    KpiBadgeComponent
  ]
})
export class SharedModule { }
