import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Course {
  id: number;
  title: string;
  description: string;
  selected: boolean;
}

interface CourseListResponse {
  courses: Course[];
}

@Injectable({ providedIn: 'root' })
export class CourseService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = 'http://localhost:8000/api';

  getCourses(): Observable<CourseListResponse> {
    return this.http.get<CourseListResponse>(`${this.apiBaseUrl}/courses/`, {
      withCredentials: true
    });
  }

  createCourse(title: string, description: string): Observable<Course> {
    return this.http.post<Course>(
      `${this.apiBaseUrl}/courses/`,
      { title, description },
      { withCredentials: true }
    );
  }

  toggleSelection(courseId: number): Observable<{ course_id: number; selected: boolean }> {
    return this.http.post<{ course_id: number; selected: boolean }>(
      `${this.apiBaseUrl}/courses/${courseId}/toggle-enrollment/`,
      {},
      { withCredentials: true }
    );
  }
}
