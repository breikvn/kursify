import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { AuthService } from '../auth.service';

@Component({
  standalone: true,
  selector: 'app-login',
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <div class="panel">
        <h1>Kursify</h1>
        <p class="intro">Login mit den Testdaten aus der Datenbank.</p>

        <div class="accounts">
          <p><strong>Admin:</strong> admin / admin123</p>
          <p><strong>Studenten:</strong> student.alex / student123</p>
          <p><strong>Studenten:</strong> student.bruce / student123</p>
        </div>

        <input [(ngModel)]="username" placeholder="Benutzername">
        <input [(ngModel)]="password" type="password" placeholder="Passwort">

        <button [disabled]="loading" (click)="login()">
          {{ loading ? 'Anmeldung...' : 'Login' }}
        </button>

        <p class="error" *ngIf="error">{{ error }}</p>
      </div>
    </div>
  `,
  styles: [`
    .page {
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, #f6efe4 0%, #dcecf2 100%);
      padding: 24px;
    }

    .panel {
      width: min(420px, 100%);
      background: rgba(255, 255, 255, 0.92);
      border-radius: 20px;
      padding: 32px;
      box-shadow: 0 18px 50px rgba(32, 52, 64, 0.15);
      display: grid;
      gap: 14px;
    }

    h1 {
      margin: 0;
      font-size: 2rem;
    }

    .intro,
    .accounts p {
      margin: 0;
    }

    .accounts {
      background: #f4f8fa;
      border-radius: 12px;
      padding: 12px;
      font-size: 0.95rem;
    }

    input,
    button {
      border-radius: 12px;
      border: 1px solid #c9d7de;
      padding: 12px 14px;
      font-size: 1rem;
    }

    button {
      border: none;
      background: #0f6c7c;
      color: white;
      font-weight: 600;
      cursor: pointer;
    }

    button:disabled {
      cursor: wait;
      opacity: 0.75;
    }

    .error {
      color: #a32121;
      margin: 0;
    }
  `]
})
export class LoginComponent {
  username = '';
  password = '';
  loading = false;
  error = '';

  constructor(
    private auth: AuthService,
    private router: Router
  ) {
    if (this.auth.isLoggedIn) {
      void this.router.navigate(['/courses']);
    }
  }

  login() {
    this.loading = true;
    this.error = '';

    this.auth.login(this.username, this.password).subscribe({
      next: () => {
        this.loading = false;
        void this.router.navigate(['/courses']);
      },
      error: (error: HttpErrorResponse) => {
        this.loading = false;
        this.error = error.error?.detail || 'Login fehlgeschlagen.';
      },
    });
  }
}
