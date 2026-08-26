import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Login } from './pages/Login';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';

import { StudentDashboard } from './pages/dashboards/StudentDashboard';
import { TeacherDashboard } from './pages/dashboards/TeacherDashboard';
import { GenericAdminDashboard } from './pages/dashboards/GenericAdminDashboard';
import { LiveMonitoring } from './pages/LiveMonitoring';

const Unauthorized = () => <div className="p-8 text-center text-red-600 font-bold text-2xl">Unauthorized Access</div>;

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
              
              <Route path="student" element={<ProtectedRoute allowedRoles={['student']} />}>
                <Route index element={<StudentDashboard />} />
                <Route path="attendance" element={<div>My Attendance</div>} />
                <Route path="classes" element={<div>My Classes</div>} />
              </Route>
              
              <Route path="teacher" element={<ProtectedRoute allowedRoles={['teacher']} />}>
                <Route index element={<TeacherDashboard />} />
                <Route path="classes" element={<div>My Classes</div>} />
                <Route path="students" element={<div>My Students</div>} />
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
                <Route path="users" element={<div>Manage Users</div>} />
              </Route>
              
              <Route path="profile" element={<div>Profile Page</div>} />
              <Route path="reports" element={<div>Reports Page</div>} />
              <Route path="monitoring" element={<LiveMonitoring />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
