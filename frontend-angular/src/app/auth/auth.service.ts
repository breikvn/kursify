import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private _username: string | null = null;

  // Demo-Zugangsdaten
  private readonly VALID_USER = {
    username: 'admin',
    password: '1234'
  };

  login(username: string, password: string): boolean {
    if (
      username === this.VALID_USER.username &&
      password === this.VALID_USER.password
    ) {
      this._username = username;
      return true;
    }
    return false;
  }

  logout() {
    this._username = null;
  }

  get isLoggedIn(): boolean {
    return this._username !== null;
  }

  get username(): string {
    return this._username ?? '';
  }
}

