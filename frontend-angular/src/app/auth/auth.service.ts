import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = 'http://localhost:8000/api';
  private readonly currentUserSubject = new BehaviorSubject<AuthUser | null>(null);
  readonly currentUser$ = this.currentUserSubject.asObservable();

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(
        `${this.apiBaseUrl}/login/`,
        { username, password },
        { withCredentials: true }
      )
      .pipe(tap((response) => this.currentUserSubject.next(response.user)));
  }

  logout(): Observable<{ success: boolean }> {
    return this.http
      .post<{ success: boolean }>(
        `${this.apiBaseUrl}/logout/`,
        {},
        { withCredentials: true }
      )
      .pipe(tap(() => this.currentUserSubject.next(null)));
  }

  restoreSession(): Observable<SessionResponse> {
    return this.http
      .get<SessionResponse>(`${this.apiBaseUrl}/session/`, { withCredentials: true })
      .pipe(tap((response) => this.currentUserSubject.next(response.user)));
  }

  createUser(payload: CreateUserPayload): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiBaseUrl}/users/`, payload, {
      withCredentials: true
    });
  }

  get currentUser(): AuthUser | null {
    return this.currentUserSubject.value;
  }

  get isLoggedIn(): boolean {
    return this.currentUser !== null;
  }

  get username(): string {
    return this.currentUser?.username ?? '';
  }

  get isAdmin(): boolean {
    return this.currentUser?.is_admin ?? false;
  }
}

export interface AuthUser {
  id: number;
  username: string;
  is_admin: boolean;
}

interface LoginResponse {
  user: AuthUser;
}

interface SessionResponse {
  user: AuthUser;
}

export interface CreateUserPayload {
  username: string;
  password: string;
  is_admin: boolean;
}
