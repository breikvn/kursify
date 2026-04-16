import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService, AuthUser } from '../auth/auth.service';

export interface Course {
  course_id: number;
  title: string;
  description: string | null;
  starts_at: string;
  ends_at: string;
  max_participants: number;
  location: string | null;
  status: string;
  active_enrollment_count: number;
  available_slots: number;
  selected: boolean;
  enrollment_status: 'PENDING' | 'CONFIRMED' | null;
  reserved_until: string | null;
  confirmed_at: string | null;
}

export interface CourseListResponse {
  results: Course[];
}

export interface UserListResponse {
  results: AuthUser[];
}

export interface CreateUserPayload {
  username: string;
  password: string;
  role: 'ADMIN' | 'STUDENT';
  display_name?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  department_id?: number | null;
}

export interface CreateCoursePayload {
  title: string;
  description: string;
  starts_at: string;
  ends_at: string;
  max_participants: number;
  location: string;
  status: string;
}

@Injectable({ providedIn: 'root' })
export class CourseService {
  constructor(
    private http: HttpClient,
    private auth: AuthService
  ) {}

  loadCourses(): Observable<CourseListResponse> {
    return this.http.get<CourseListResponse>(`${this.auth.apiUrl}/courses`, {
      headers: this.auth.authHeaders,
    });
  }

  enroll(courseId: number): Observable<unknown> {
    return this.http.post(
      `${this.auth.apiUrl}/courses/${courseId}/enroll`,
      {},
      { headers: this.auth.authHeaders }
    );
  }

  unenroll(courseId: number): Observable<unknown> {
    return this.http.post(
      `${this.auth.apiUrl}/courses/${courseId}/unenroll`,
      {},
      { headers: this.auth.authHeaders }
    );
  }

  loadUsers(): Observable<UserListResponse> {
    return this.http.get<UserListResponse>(`${this.auth.apiUrl}/users`, {
      headers: this.auth.authHeaders,
    });
  }

  createUser(payload: CreateUserPayload): Observable<AuthUser> {
    return this.http.post<AuthUser>(`${this.auth.apiUrl}/users`, payload, {
      headers: this.auth.authHeaders,
    });
  }

  createCourse(payload: CreateCoursePayload): Observable<Course> {
    return this.http.post<Course>(`${this.auth.apiUrl}/courses`, payload, {
      headers: this.auth.authHeaders,
    });
  }
}
