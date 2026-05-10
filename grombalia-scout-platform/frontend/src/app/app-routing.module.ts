import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ActivityPlanningComponent } from './pages/activity-planning/activity-planning.component';
import { AnomalyComponent } from './pages/anomaly/anomaly.component';
import { ClassificationComponent } from './pages/classification/classification.component';
import { ForecastComponent } from './pages/forecast/forecast.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login/:role', component: LoginComponent },
  { path: 'dashboard/:role', component: DashboardComponent },
  { path: 'recommendation', component: ActivityPlanningComponent },
  { path: 'anomaly', component: AnomalyComponent },
  { path: 'forecast', component: ForecastComponent },
  { path: 'classification', component: ClassificationComponent },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
