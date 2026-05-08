/* src/app/shared/shared.module.ts */
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AudioButtonComponent } from './components/audio-button/audio-button.component';

@NgModule({
  declarations: [
    AudioButtonComponent
  ],
  imports: [
    CommonModule
  ],
  exports: [
    CommonModule,
    AudioButtonComponent
  ]
})
export class SharedModule { }
