import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { CourseCardComponent } from './course-card.component';
import { AuthService } from '../auth/auth.service';

interface Course {
  id: number;
  title: string;
  description: string;
  selected: boolean;
}

@Component({
  standalone: true,
  selector: 'app-course-list',
  imports: [CommonModule, CourseCardComponent],
  template: `
    <header class="topbar">
      <span>👋 Willkommen, <strong>{{ auth.username }}</strong></span>
      <button (click)="logout()">Logout</button>
    </header>

    <h2>Kurse auswählen</h2>

    <div class="grid">
      <app-course-card
        *ngFor="let course of courses"
        [course]="course"
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

    .grid {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }
  `]
})
export class CourseListComponent {
  courses: Course[] = [
    { id: 1, title: 'Angular Basics', description: 'Grundlagen', selected: false },
    { id: 2, title: 'TypeScript', description: 'Typen & Interfaces', selected: false },
    { id: 3, title: 'RxJS', description: 'Observables', selected: false }
  ];

  constructor(
    public auth: AuthService,
    private router: Router
  ) {}

  toggleCourse(id: number) {
    const course = this.courses.find(c => c.id === id);
    if (course) course.selected = !course.selected;
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
