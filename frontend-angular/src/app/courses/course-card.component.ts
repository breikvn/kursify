import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface Course {
  id: number;
  title: string;
  description: string;
  selected: boolean;
}

@Component({
  selector: 'app-course-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card">
      <h3>{{ course.title }}</h3>
      <p>{{ course.description }}</p>

      <button (click)="toggle.emit(course.id)">
        {{ course.selected ? 'Abwählen' : 'Wählen' }}
      </button>
    </div>
  `,
  styles: [`
    .card {
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px;
      width: 220px;
      box-shadow: 0 2px 6px rgba(0,0,0,.1);
    }

    button {
      margin-top: 12px;
      width: 100%;
      padding: 8px;
      border: none;
      border-radius: 6px;
      background: #1976d2;
      color: white;
      cursor: pointer;
    }
  `]
})
export class CourseCardComponent {
  @Input() course!: Course;
  @Output() toggle = new EventEmitter<number>();
}

