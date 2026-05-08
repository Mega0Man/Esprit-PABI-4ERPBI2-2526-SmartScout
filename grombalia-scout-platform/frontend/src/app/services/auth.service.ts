import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';

interface User {
  id: number;
  username: string;
  role: string;
  created_at: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8090';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    if (token && user) {
      this.currentUserSubject.next(JSON.parse(user));
    }
  }

  login(username: string, password: string): Observable<AuthResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    return this.http.post<AuthResponse>(`${this.apiUrl}/token`, formData).pipe(
      tap(response => {
        this.setSession(response);
      })
    );
  }

  loginByFace(username: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/face-token?username=${username}`, {}).pipe(
      tap(response => {
        this.setSession(response);
      })
    );
  }

  signup(signupData: { 
    username: string; 
    password: string; 
    role: string; 
    national_id: string; 
    face_descriptor?: number[] 
  }): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/signup`, signupData);
  }

  getFaceDescriptors(): Observable<Record<string, number[]>> {
    return this.http.get<Record<string, number[]>>(`${this.apiUrl}/face-descriptors`);
  }

  private setSession(response: AuthResponse): void {
    localStorage.setItem('token', response.access_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    this.currentUserSubject.next(response.user);
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.currentUserSubject.next(null);
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }
}
