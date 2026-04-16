import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { CourseCardComponent } from './course-card.component';
import { AuthService, AuthUser } from '../auth/auth.service';
import { Course, CourseService, CreateCoursePayload, CreateUserPayload } from './course.service';

@Component({
  standalone: true,
  selector: 'app-course-list',
  imports: [CommonModule, FormsModule, CourseCardComponent],
  template: `
    <div class="page">
      <header class="topbar">
        <div>
          <p class="eyebrow">{{ auth.user?.role === 'ADMIN' ? 'Adminbereich' : 'Studentenbereich' }}</p>
          <h1>{{ auth.username }}</h1>
        </div>
        <button class="secondary" (click)="logout()">Logout</button>
      </header>

      <p class="message" *ngIf="message">{{ message }}</p>
      <p class="error" *ngIf="error">{{ error }}</p>

      <section *ngIf="auth.isStudent" class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Kurse</p>
            <h2>Aus Datenbank geladen</h2>
          </div>
          <button class="secondary" (click)="loadCourses()">Aktualisieren</button>
        </div>

        <div class="grid">
          <app-course-card
            *ngFor="let course of courses"
            [course]="course"
            [loading]="busyCourseId === course.course_id"
            (toggle)="toggleCourse($event)">
          </app-course-card>
        </div>
      </section>

      <section *ngIf="auth.isAdmin" class="admin-layout">
        <div class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Benutzer</p>
              <h2>Testnutzer und neue Accounts</h2>
            </div>
            <button class="secondary" (click)="loadUsers()">Neu laden</button>
          </div>

          <form class="form" (ngSubmit)="createUser()">
            <label>
              Rolle
              <select [(ngModel)]="userForm.role" name="role">
                <option value="STUDENT">Student</option>
                <option value="ADMIN">Admin</option>
              </select>
            </label>

            <label>
              Username
              <input [(ngModel)]="userForm.username" name="username">
            </label>

            <label>
              Passwort
              <input [(ngModel)]="userForm.password" name="password" type="password">
            </label>

            <label *ngIf="userForm.role === 'ADMIN'">
              Anzeigename
              <input [(ngModel)]="userForm.display_name" name="display_name">
            </label>

            <label *ngIf="userForm.role === 'STUDENT'">
              Vorname
              <input [(ngModel)]="userForm.first_name" name="first_name">
            </label>

            <label *ngIf="userForm.role === 'STUDENT'">
              Nachname
              <input [(ngModel)]="userForm.last_name" name="last_name">
            </label>

            <label *ngIf="userForm.role === 'STUDENT'">
              E-Mail
              <input [(ngModel)]="userForm.email" name="email">
            </label>

            <button type="submit">Benutzer anlegen</button>
          </form>

          <div class="list">
            <article *ngFor="let user of users" class="list-item">
              <strong>{{ user.display_name || user.username }}</strong>
              <span>{{ user.role }}</span>
              <span>{{ user.username }}</span>
              <span *ngIf="user.employee">{{ user.employee.email }}</span>
            </article>
          </div>
        </div>

        <div class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Kurse</p>
              <h2>Kurse anlegen und prüfen</h2>
            </div>
            <button class="secondary" (click)="loadCourses()">Neu laden</button>
          </div>

          <form class="form" (ngSubmit)="createCourse()">
            <label>
              Titel
              <input [(ngModel)]="courseForm.title" name="title">
            </label>

            <label>
              Beschreibung
              <textarea [(ngModel)]="courseForm.description" name="description"></textarea>
            </label>

            <label>
              Start
              <input [(ngModel)]="courseForm.starts_at" name="starts_at" type="datetime-local">
            </label>

            <label>
              Ende
              <input [(ngModel)]="courseForm.ends_at" name="ends_at" type="datetime-local">
            </label>

            <label>
              Max. Teilnehmer
              <input [(ngModel)]="courseForm.max_participants" name="max_participants" type="number">
            </label>

            <label>
              Ort
              <input [(ngModel)]="courseForm.location" name="location">
            </label>

            <button type="submit">Kurs anlegen</button>
          </form>

          <div class="grid admin-grid">
            <app-course-card
              *ngFor="let course of courses"
              [course]="course"
              [showActions]="false">
            </app-course-card>
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .page {
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(236, 186, 108, 0.26), transparent 30%),
        linear-gradient(180deg, #f7f1e6 0%, #edf3f5 100%);
      padding: 28px;
      color: #16303b;
    }

    .topbar,
    .panel-head,
    .list-item {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }

    .topbar {
      margin-bottom: 24px;
    }

    .panel,
    .list-item {
      background: rgba(255, 255, 255, 0.92);
      border-radius: 22px;
      box-shadow: 0 16px 44px rgba(20, 45, 56, 0.08);
    }

    .panel {
      padding: 24px;
    }

    .admin-layout {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 24px;
    }

    .eyebrow {
      margin: 0 0 6px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 0.78rem;
      color: #55707a;
    }

    h1,
    h2,
    .message,
    .error {
      margin: 0;
    }

    .message,
    .error {
      margin-bottom: 18px;
      padding: 12px 14px;
      border-radius: 12px;
    }

    .message {
      background: #def2e6;
      color: #1a5a38;
    }

    .error {
      background: #f9e0e0;
      color: #8f1f1f;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 18px;
      margin-top: 20px;
    }

    .admin-grid {
      max-height: 720px;
      overflow: auto;
    }

    .form {
      display: grid;
      gap: 14px;
      margin-top: 20px;
    }

    label {
      display: grid;
      gap: 6px;
      font-weight: 600;
    }

    input,
    textarea,
    select,
    button {
      border-radius: 12px;
      border: 1px solid #cbdae0;
      padding: 11px 13px;
      font: inherit;
    }

    textarea {
      min-height: 96px;
      resize: vertical;
    }

    button {
      border: none;
      background: #0f6c7c;
      color: white;
      font-weight: 700;
      cursor: pointer;
    }

    .secondary {
      background: #dbe7eb;
      color: #183742;
    }

    .list {
      display: grid;
      gap: 12px;
      margin-top: 20px;
    }

    .list-item {
      padding: 14px 16px;
      flex-wrap: wrap;
    }
  `]
})
export class CourseListComponent implements OnInit {
  courses: Course[] = [];
  users: AuthUser[] = [];
  busyCourseId: number | null = null;
  message = '';
  error = '';

  userForm: CreateUserPayload = {
    username: '',
    password: '',
    role: 'STUDENT',
    display_name: '',
    first_name: '',
    last_name: '',
    email: '',
  };

  courseForm: CreateCoursePayload = {
    title: '',
    description: '',
    starts_at: '',
    ends_at: '',
    max_participants: 12,
    location: '',
    status: 'OPEN',
  };

  constructor(
    public auth: AuthService,
    private courseService: CourseService,
    private router: Router
  ) {}

  ngOnInit() {
    if (!this.auth.isLoggedIn) {
      void this.router.navigate(['/login']);
      return;
    }

    this.loadCourses();
    if (this.auth.isAdmin) {
      this.loadUsers();
    }
  }

  loadCourses() {
    this.clearAlerts();
    this.courseService.loadCourses().subscribe({
      next: (response) => {
        this.courses = response.results;
      },
      error: (error: HttpErrorResponse) => this.handleError(error),
    });
  }

  loadUsers() {
    this.clearAlerts();
    this.courseService.loadUsers().subscribe({
      next: (response) => {
        this.users = response.results;
      },
      error: (error: HttpErrorResponse) => this.handleError(error),
    });
  }

  toggleCourse(courseId: number) {
    const course = this.courses.find((entry) => entry.course_id === courseId);
    if (!course) {
      return;
    }

    this.clearAlerts();
    this.busyCourseId = courseId;

    const request = course.selected
      ? this.courseService.unenroll(courseId)
      : this.courseService.enroll(courseId);

    request.subscribe({
      next: () => {
        this.busyCourseId = null;
        this.message = course.selected
          ? 'Kurs abgewählt.'
          : 'Reservierung angelegt. Bitte Teilnahme innerhalb von 24 Stunden per E-Mail bestätigen.';
        this.loadCourses();
      },
      error: (error: HttpErrorResponse) => {
        this.busyCourseId = null;
        this.handleError(error);
      },
    });
  }

  createUser() {
    this.clearAlerts();
    this.courseService.createUser(this.userForm).subscribe({
      next: () => {
        this.message = 'Benutzer angelegt.';
        this.userForm = {
          username: '',
          password: '',
          role: 'STUDENT',
          display_name: '',
          first_name: '',
          last_name: '',
          email: '',
        };
        this.loadUsers();
      },
      error: (error: HttpErrorResponse) => this.handleError(error),
    });
  }

  createCourse() {
    this.clearAlerts();
    this.courseService.createCourse(this.courseForm).subscribe({
      next: () => {
        this.message = 'Kurs angelegt.';
        this.courseForm = {
          title: '',
          description: '',
          starts_at: '',
          ends_at: '',
          max_participants: 12,
          location: '',
          status: 'OPEN',
        };
        this.loadCourses();
      },
      error: (error: HttpErrorResponse) => this.handleError(error),
    });
  }

  logout() {
    this.auth.logout().subscribe({
      next: () => {
        void this.router.navigate(['/login']);
      },
      error: () => {
        this.auth.clearSession();
        void this.router.navigate(['/login']);
      },
    });
  }

  private clearAlerts() {
    this.message = '';
    this.error = '';
  }

  private handleError(error: HttpErrorResponse) {
    this.error = error.error?.detail || 'Aktion fehlgeschlagen.';
    if (error.status === 401) {
      this.auth.clearSession();
      void this.router.navigate(['/login']);
    }
  }
}
