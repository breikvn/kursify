import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { Course } from './course.service';

@Component({
  selector: 'app-course-card',
  standalone: true,
  imports: [CommonModule, DatePipe],
  template: `
    <article class="card">
      <div class="badge" [class.selected]="course.selected" [class.pending]="course.enrollment_status === 'PENDING'">
        {{ badgeLabel }}
      </div>

      <h3>{{ course.title }}</h3>
      <p class="description">{{ course.description || 'Keine Beschreibung vorhanden.' }}</p>

      <dl>
        <div>
          <dt>Start</dt>
          <dd>{{ course.starts_at | date: 'dd.MM.yyyy HH:mm' }}</dd>
        </div>
        <div>
          <dt>Ort</dt>
          <dd>{{ course.location || 'TBD' }}</dd>
        </div>
        <div>
          <dt>Plätze</dt>
          <dd>{{ course.available_slots }} frei / {{ course.max_participants }}</dd>
        </div>
        <div *ngIf="course.enrollment_status === 'PENDING' && course.reserved_until">
          <dt>Bestaetigen bis</dt>
          <dd>{{ course.reserved_until | date: 'dd.MM.yyyy HH:mm' }}</dd>
        </div>
      </dl>

      <button
        *ngIf="showActions"
        [disabled]="loading || (!course.selected && course.available_slots === 0)"
        (click)="toggle.emit(course.course_id)">
        {{ loading ? 'Speichern...' : buttonLabel }}
      </button>
    </article>
  `,
  styles: [`
    .card {
      background: white;
      border-radius: 18px;
      padding: 20px;
      box-shadow: 0 12px 28px rgba(20, 45, 56, 0.08);
      display: grid;
      gap: 14px;
    }

    .badge {
      justify-self: start;
      padding: 6px 10px;
      border-radius: 999px;
      background: #eff4f6;
      color: #23414d;
      font-size: 0.85rem;
      font-weight: 700;
    }

    .badge.selected {
      background: #dff4e7;
      color: #165c34;
    }

    .badge.pending {
      background: #fff0ce;
      color: #8a5b00;
    }

    h3,
    .description,
    dl,
    dd {
      margin: 0;
    }

    dl {
      display: grid;
      gap: 10px;
    }

    dt {
      font-size: 0.8rem;
      text-transform: uppercase;
      color: #5d7580;
      margin-bottom: 2px;
    }

    button {
      border: none;
      border-radius: 12px;
      padding: 12px 14px;
      background: #0f6c7c;
      color: white;
      font-weight: 700;
      cursor: pointer;
    }

    button:disabled {
      opacity: 0.65;
      cursor: not-allowed;
    }
  `]
})
export class CourseCardComponent {
  @Input() course!: Course;
  @Input() showActions = true;
  @Input() loading = false;
  @Output() toggle = new EventEmitter<number>();

  get badgeLabel(): string {
    if (this.course.enrollment_status === 'PENDING') {
      return 'Reserviert';
    }
    if (this.course.enrollment_status === 'CONFIRMED') {
      return 'Gebucht';
    }
    return 'Offen';
  }

  get buttonLabel(): string {
    if (!this.course.selected) {
      return 'Wählen';
    }
    if (this.course.enrollment_status === 'PENDING') {
      return 'Reservierung stornieren';
    }
    return 'Abwählen';
  }
}
