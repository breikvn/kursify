import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  standalone: true,
  selector: 'app-login',
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login">
      <h2>Login</h2>

      <input
        [(ngModel)]="username"
        placeholder="Username"
      >

      <input
        [(ngModel)]="password"
        type="password"
        placeholder="Passwort"
      >

      <button (click)="login()">Login</button>

      <p class="error" *ngIf="error">
        ❌ Benutzername oder Passwort falsch
      </p>
    </div>
  `,
  styles: [`
    .login {
      max-width: 300px;
      margin: 100px auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .error {
      color: red;
      font-size: 14px;
    }
  `]
})
export class LoginComponent {
  username = '';
  password = '';
  error = false;

  constructor(
    private auth: AuthService,
    private router: Router
  ) {}

  login() {
    this.error = false;

    const success = this.auth.login(this.username, this.password);

    if (success) {
      this.router.navigate(['/courses']);
    } else {
      this.error = true;
    }
  }
}
