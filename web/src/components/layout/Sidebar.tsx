import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, 
  Users, 
  BookOpen, 
  CalendarCheck, 
  Settings, 
  Activity,
  LogOut,
  GraduationCap
} from 'lucide-react';
import { auth } from '../../firebase/config';

export const Sidebar: React.FC = () => {
  const { profile } = useAuth();
  
  if (!profile) return null;

  const role = profile.role;

  const handleLogout = () => {
    auth.signOut();
  };

  const linkClass = ({ isActive }: { isActive: boolean }) => 
    `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
      isActive 
        ? 'bg-primary-600 text-white' 
        : 'text-gray-600 hover:bg-gray-100'
    }`;

  return (
    <div className="w-64 bg-white h-screen border-r border-gray-200 flex flex-col fixed left-0 top-0">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3 text-primary-600">
          <GraduationCap size={32} />
          <span className="text-xl font-bold">Edge AI Univ</span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        <NavLink to={`/dashboard/${role}`} className={linkClass} end>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>

        {role === 'student' && (
          <>
            <NavLink to="/dashboard/student/attendance" className={linkClass}>
              <CalendarCheck size={20} />
              <span>My Attendance</span>
            </NavLink>
            <NavLink to="/dashboard/student/classes" className={linkClass}>
              <BookOpen size={20} />
              <span>My Classes</span>
            </NavLink>
          </>
        )}

        {role === 'teacher' && (
          <>
            <NavLink to="/dashboard/teacher/classes" className={linkClass}>
              <BookOpen size={20} />
              <span>My Classes</span>
            </NavLink>
            <NavLink to="/dashboard/teacher/students" className={linkClass}>
              <Users size={20} />
              <span>Students</span>
            </NavLink>
          </>
        )}

        {['hod', 'dean', 'vc', 'admin'].includes(role) && (
          <>
            <NavLink to="/dashboard/reports" className={linkClass}>
              <CalendarCheck size={20} />
              <span>Reports</span>
            </NavLink>
            <NavLink to="/dashboard/monitoring" className={linkClass}>
              <Activity size={20} />
              <span>Live Monitoring</span>
            </NavLink>
          </>
        )}

        {role === 'admin' && (
          <NavLink to="/dashboard/admin/users" className={linkClass}>
            <Users size={20} />
            <span>Manage Users</span>
          </NavLink>
        )}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <NavLink to="/dashboard/profile" className={linkClass}>
          <Settings size={20} />
          <span>Profile</span>
        </NavLink>
        <button 
          onClick={handleLogout}
          className="w-full flex items-center space-x-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors mt-2"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};
