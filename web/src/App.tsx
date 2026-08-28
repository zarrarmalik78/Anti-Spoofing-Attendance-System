import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Login } from './pages/Login';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';

import { StudentDashboard } from './pages/dashboards/StudentDashboard';
import { TeacherDashboard } from './pages/dashboards/TeacherDashboard';
import { GenericAdminDashboard } from './pages/dashboards/GenericAdminDashboard';
import { LiveMonitoring } from './pages/LiveMonitoring';
import { StudentsPage } from './pages/StudentsPage';
import { TeachersPage } from './pages/TeachersPage';
import { UsersPage } from './pages/UsersPage';
import { AcademicUnitsPage } from './pages/AcademicUnitsPage';
import { CoursesClassesPage } from './pages/CoursesClassesPage';
import { AttendancePage } from './pages/AttendancePage';
import { ReportsPage } from './pages/ReportsPage';
import { ProfilePage } from './pages/ProfilePage';

const Unauthorized = () => (
  <div className="p-8 text-center text-rose-600 font-bold text-2xl">
    Unauthorized Access — Restricted Institutional Scope
  </div>
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/unauthorized" element={<Unauthorized />} />
          
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          <Route path="/dashboard" element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              {/* Fallback */}
              <Route index element={<Navigate to="profile" replace />} />
              
              {/* Role Dashboards */}
              <Route path="student" element={<ProtectedRoute allowedRoles={['student']} />}>
                <Route index element={<StudentDashboard />} />
              </Route>
              
              <Route path="teacher" element={<ProtectedRoute allowedRoles={['teacher']} />}>
                <Route index element={<TeacherDashboard />} />
              </Route>
              
              <Route path="hod" element={<ProtectedRoute allowedRoles={['hod']} />}>
                <Route index element={<GenericAdminDashboard />} />
              </Route>

              <Route path="dean" element={<ProtectedRoute allowedRoles={['dean']} />}>
                <Route index element={<GenericAdminDashboard />} />
              </Route>

              <Route path="vc" element={<ProtectedRoute allowedRoles={['vc']} />}>
                <Route index element={<GenericAdminDashboard />} />
              </Route>

              <Route path="admin" element={<ProtectedRoute allowedRoles={['admin']} />}>
                <Route index element={<GenericAdminDashboard />} />
              </Route>
              
              {/* University Management Pages */}
              <Route path="students" element={<ProtectedRoute allowedRoles={['admin', 'vc', 'dean', 'hod', 'teacher']} />}>
                <Route index element={<StudentsPage />} />
              </Route>

              <Route path="teachers" element={<ProtectedRoute allowedRoles={['admin', 'vc', 'dean', 'hod']} />}>
                <Route index element={<TeachersPage />} />
              </Route>

              <Route path="users" element={<ProtectedRoute allowedRoles={['admin', 'vc', 'dean', 'hod']} />}>
                <Route index element={<UsersPage />} />
              </Route>

              <Route path="academic-units" element={<ProtectedRoute allowedRoles={['admin', 'vc', 'dean', 'hod']} />}>
                <Route index element={<AcademicUnitsPage />} />
              </Route>

              <Route path="courses-classes" element={<CoursesClassesPage />} />
              <Route path="attendance" element={<AttendancePage />} />
              
              <Route path="reports" element={<ProtectedRoute allowedRoles={['admin', 'vc', 'dean', 'hod']} />}>
                <Route index element={<ReportsPage />} />
              </Route>

              <Route path="monitoring" element={<ProtectedRoute allowedRoles={['admin', 'vc', 'dean', 'hod', 'teacher']} />}>
                <Route index element={<LiveMonitoring />} />
              </Route>

              <Route path="profile" element={<ProfilePage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
