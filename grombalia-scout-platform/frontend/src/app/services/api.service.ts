import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8090';

  constructor(private http: HttpClient, private authService: AuthService) { }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  forecasting(input: { months: number }): Observable<any> {
    return this.http.post(`${this.apiUrl}/ml/forecasting`, input, {
      headers: this.getHeaders()
    });
  }

  classification(input: { age: number; gender: string; unit: string; membership_years: number }): Observable<any> {
    return this.http.post(`${this.apiUrl}/ml/classification`, input, {
      headers: this.getHeaders()
    });
  }

  anomaly(input: { amount: number; transaction_type: string; category: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/ml/anomaly`, input, {
      headers: this.getHeaders()
    });
  }

  recommendation(input: { scout_id: number; activity_preferences: string[] }): Observable<any> {
    return this.http.post(`${this.apiUrl}/ml/recommendation`, input, {
      headers: this.getHeaders()
    });
  }
}
