import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../auth/auth.service';
import { Course, CourseService } from './course.service';
import { CourseCardComponent } from './course-card.component';

@Component({
  standalone: true,
  selector: 'app-course-list',
  imports: [CommonModule, FormsModule, CourseCardComponent],
  template: `
    <header class="topbar">
      <span>
        Willkommen, <strong>{{ auth.username }}</strong>
        <small *ngIf="auth.isAdmin">(Admin)</small>
      </span>
      <button (click)="logout()">Logout</button>
    </header>

    <p class="message" *ngIf="message">{{ message }}</p>
    <p class="error" *ngIf="error">{{ error }}</p>

    <section class="admin-panel" *ngIf="auth.isAdmin">
      <h2>Kurs anlegen</h2>
      <div class="form-grid">
        <input [(ngModel)]="newCourseTitle" placeholder="Kurstitel">
        <textarea [(ngModel)]="newCourseDescription" placeholder="Beschreibung"></textarea>
        <button (click)="createCourse()">Kurs speichern</button>
      </div>

      <h2>Neuen Nutzer anlegen</h2>
      <div class="form-grid">
        <input [(ngModel)]="newUsername" placeholder="Benutzername">
        <input [(ngModel)]="newPassword" type="password" placeholder="Passwort">
        <label class="checkbox">
          <input [(ngModel)]="newUserIsAdmin" type="checkbox">
          Adminrechte vergeben
        </label>
        <button (click)="createUser()">Nutzer speichern</button>
      </div>
    </section>

    <h2>{{ auth.isAdmin ? 'Vorhandene Kurse' : 'Kurse auswählen' }}</h2>

    <div class="grid">
      <app-course-card
        *ngFor="let course of courses"
        [course]="course"
        [showSelectionButton]="!auth.isAdmin"
        (toggle)="toggleCourse($event)">
      </app-course-card>
    </div>
  `,
  styles: [`
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px;
      background: #f5f5f5;
      margin-bottom: 16px;
    }

    button {
      padding: 6px 12px;
      cursor: pointer;
    }

    .admin-panel {
      display: grid;
      gap: 12px;
      margin-bottom: 24px;
      padding: 16px;
      background: #f5f5f5;
      border-radius: 8px;
    }

    .form-grid {
      display: grid;
      gap: 10px;
      max-width: 520px;
    }

    input, textarea {
      padding: 10px;
      font: inherit;
    }

    textarea {
      min-height: 90px;
      resize: vertical;
    }

    .checkbox {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .message {
      color: #146c2e;
    }

    .error {
      color: #b42318;
    }

    .grid {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }
  `]
})
export class CourseListComponent {
  courses: Course[] = [];
  newCourseTitle = '';
  newCourseDescription = '';
  newUsername = '';
  newPassword = '';
  newUserIsAdmin = false;
  message = '';
  error = '';

  constructor(
    public auth: AuthService,
    private courseService: CourseService,
    private router: Router
  ) {
    this.auth.restoreSession().subscribe({
      next: () => this.loadCourses(),
      error: () => this.router.navigate(['/login'])
    });
  }

  toggleCourse(id: number) {
    this.error = '';
    this.message = '';
    this.courseService.toggleSelection(id).subscribe({
      next: (response) => {
        const course = this.courses.find((entry) => entry.id === response.course_id);
        if (course) {
          course.selected = response.selected;
        }
      },
      error: () => {
        this.error = 'Die Kurswahl konnte nicht gespeichert werden.';
      }
    });
  }

  logout() {
    this.auth.logout().subscribe({
      next: () => this.router.navigate(['/login']),
      error: () => this.router.navigate(['/login'])
    });
  }

  createCourse() {
    this.error = '';
    this.message = '';
    this.courseService.createCourse(this.newCourseTitle, this.newCourseDescription).subscribe({
      next: (course) => {
        this.courses = [...this.courses, course].sort((a, b) => a.title.localeCompare(b.title));
        this.newCourseTitle = '';
        this.newCourseDescription = '';
        this.message = 'Kurs wurde angelegt.';
      },
      error: () => {
        this.error = 'Der Kurs konnte nicht angelegt werden.';
      }
    });
  }

  createUser() {
    this.error = '';
    this.message = '';
    this.auth.createUser({
      username: this.newUsername,
      password: this.newPassword,
      is_admin: this.newUserIsAdmin
    }).subscribe({
      next: () => {
        this.newUsername = '';
        this.newPassword = '';
        this.newUserIsAdmin = false;
        this.message = 'Nutzer wurde angelegt.';
      },
      error: () => {
        this.error = 'Der Nutzer konnte nicht angelegt werden.';
      }
    });
  }

  private loadCourses() {
    this.courseService.getCourses().subscribe({
      next: (response) => {
        this.courses = response.courses;
      },
      error: () => {
        this.error = 'Die Kurse konnten nicht geladen werden.';
      }
    });
  }
}
