import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { FaceRecognitionComponent } from './face-recognition/face-recognition.component';

import { ActivityPlanningComponent } from './pages/activity-planning/activity-planning.component';
import { AnomalyComponent } from './pages/anomaly/anomaly.component';
import { ClassificationComponent } from './pages/classification/classification.component';
import { ForecastComponent } from './pages/forecast/forecast.component';

import { SharedModule } from './shared/shared.module';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    LoginComponent,
    DashboardComponent,
    FaceRecognitionComponent,
    ActivityPlanningComponent,
    AnomalyComponent,
    ClassificationComponent,
    ForecastComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    SharedModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
