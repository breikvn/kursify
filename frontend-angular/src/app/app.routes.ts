import { Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login.component';
import { CourseListComponent } from './courses/course-list.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'courses', component: CourseListComponent },
  { path: '**', redirectTo: 'login' }
];
