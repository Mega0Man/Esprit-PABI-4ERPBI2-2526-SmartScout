/* src/app/shared/shared.module.ts */
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AudioButtonComponent } from './components/audio-button/audio-button.component';
import { ScoutAssistantComponent } from './components/scout-assistant/scout-assistant.component';

@NgModule({
  declarations: [
    AudioButtonComponent,
    ScoutAssistantComponent
  ],
  imports: [
    CommonModule,
    FormsModule
  ],
  exports: [
    CommonModule,
    FormsModule,
    AudioButtonComponent,
    ScoutAssistantComponent
  ]
})
export class SharedModule { }
