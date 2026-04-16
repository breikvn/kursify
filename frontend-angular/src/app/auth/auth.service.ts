import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export interface Employee {
  employee_id: number;
  first_name: string | null;
  last_name: string;
  email: string;
  phone_number: string | null;
  hire_date: string | null;
  job_id: string;
  department_id: number | null;
}

export interface AuthUser {
  user_id: number;
  username: string;
  role: 'ADMIN' | 'STUDENT';
  display_name: string | null;
  employee: Employee | null;
  token?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiBaseUrl = 'http://localhost:8000/api';
  private readonly storageKey = 'kursify.auth';
  private _user: AuthUser | null = this.readStoredUser();

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<AuthUser> {
    return this.http
      .post<AuthUser>(`${this.apiBaseUrl}/auth/login`, { username, password })
      .pipe(tap((user) => this.storeUser(user)));
  }

  logout(): Observable<unknown> {
    if (!this._user) {
      this.clearUser();
      return this.http.post(`${this.apiBaseUrl}/auth/logout`, {});
    }

    return this.http
      .post(`${this.apiBaseUrl}/auth/logout`, {}, { headers: this.authHeaders })
      .pipe(tap(() => this.clearUser()));
  }

  clearSession() {
    this.clearUser();
  }

  get authHeaders(): HttpHeaders {
    const token = this._user?.token ?? '';
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
    });
  }

  get apiUrl(): string {
    return this.apiBaseUrl;
  }

  get isLoggedIn(): boolean {
    return this._user !== null;
  }

  get user(): AuthUser | null {
    return this._user;
  }

  get username(): string {
    return this._user?.display_name || this._user?.username || '';
  }

  get isAdmin(): boolean {
    return this._user?.role === 'ADMIN';
  }

  get isStudent(): boolean {
    return this._user?.role === 'STUDENT';
  }

  private storeUser(user: AuthUser) {
    this._user = user;
    localStorage.setItem(this.storageKey, JSON.stringify(user));
  }

  private clearUser() {
    this._user = null;
    localStorage.removeItem(this.storageKey);
  }

  private readStoredUser(): AuthUser | null {
    const rawValue = localStorage.getItem(this.storageKey);
    if (!rawValue) {
      return null;
    }

    try {
      return JSON.parse(rawValue) as AuthUser;
    } catch {
      localStorage.removeItem(this.storageKey);
      return null;
    }
  }
}
