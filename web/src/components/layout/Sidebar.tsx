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
  Sparkles,
  Camera,
  X
} from 'lucide-react';
import { auth } from '../../firebase/config';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = false, onClose }) => {
  const { profile } = useAuth();

  if (!profile) return null;

  const role = profile.role;

  const handleLogout = () => {
    auth.signOut();
  };

  const handleNavClick = () => {
    if (onClose) {
      onClose();
    }
  };

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
      isActive
        ? 'bg-brand-50 text-brand-600 shadow-sm shadow-brand-500/10'
        : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
    }`;

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden animate-fade-in"
          onClick={onClose}
        />
      )}

      <aside
        className={`w-64 bg-white h-screen border-r border-slate-100 flex flex-col fixed left-0 top-0 z-50 select-none transition-transform duration-300 ${
          isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-brand-600 text-white flex items-center justify-center shadow-md shadow-brand-500/30">
              <Sparkles size={20} className="animate-pulse" />
            </div>
            <div>
              <h1 className="text-base font-black text-slate-900 tracking-tight flex items-center gap-1.5">
                Edge AI <span className="text-[10px] uppercase font-extrabold px-1.5 py-0.5 rounded bg-brand-100 text-brand-700">OS</span>
              </h1>
              <p className="text-[11px] font-medium text-slate-400">Biometric Attendance</p>
            </div>
          </div>

          {/* Close button for Mobile */}
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              aria-label="Close sidebar"
            >
              <X size={18} />
            </button>
          )}
        </div>

      {/* Navigation Links */}
      <div className="flex-1 px-4 py-4 space-y-5 overflow-y-auto">
        {/* Main Section */}
        <div>
          <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
            Main
          </p>
          <NavLink to={`/dashboard/${role}`} onClick={handleNavClick} className={linkClass} end>
            <div className="flex items-center gap-3">
              <LayoutDashboard size={18} />
              <span>Dashboard</span>
            </div>
          </NavLink>
        </div>

        {/* Student Specific */}
        {role === 'student' && (
          <div>
            <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
              My Academic
            </p>
            <div className="space-y-1">
              <NavLink to="/dashboard/attendance" className={linkClass}>
                <div className="flex items-center gap-3">
                  <CalendarCheck size={18} />
                  <span>My Attendance</span>
                </div>
              </NavLink>
              <NavLink to="/dashboard/courses-classes" className={linkClass}>
                <div className="flex items-center gap-3">
                  <BookOpen size={18} />
                  <span>Enrolled Classes</span>
                </div>
              </NavLink>
            </div>
          </div>
        )}

        {/* Teacher Specific */}
        {role === 'teacher' && (
          <div>
            <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
              Teaching Scope
            </p>
            <div className="space-y-1">
              <NavLink to="/dashboard/courses-classes" className={linkClass}>
                <div className="flex items-center gap-3">
                  <BookOpen size={18} />
                  <span>Assigned Classes</span>
                </div>
              </NavLink>
              <NavLink to="/dashboard/students" className={linkClass}>
                <div className="flex items-center gap-3">
                  <Users size={18} />
                  <span>Class Rosters</span>
                </div>
              </NavLink>
              <NavLink to="/dashboard/attendance" className={linkClass}>
                <div className="flex items-center gap-3">
                  <CalendarCheck size={18} />
                  <span>Attendance Logs</span>
                </div>
              </NavLink>
            </div>
          </div>
        )}

        {/* Academic Hierarchy & Administration (HOD, Dean, VC, Admin) */}
        {['hod', 'dean', 'vc', 'admin'].includes(role) && (
          <>
            {/* University Structure */}
            <div>
              <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
                University Structure
              </p>
              <div className="space-y-1">
                <NavLink to="/dashboard/academic-units" className={linkClass}>
                  <div className="flex items-center gap-3">
                    <BookOpen size={18} />
                    <span>Academic Units</span>
                  </div>
                </NavLink>
                <NavLink to="/dashboard/courses-classes" className={linkClass}>
                  <div className="flex items-center gap-3">
                    <CalendarCheck size={18} />
                    <span>Courses & Classes</span>
                  </div>
                </NavLink>
              </div>
            </div>

            {/* People & Roles */}
            <div>
              <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
                People & Access
              </p>
              <div className="space-y-1">
                <NavLink to="/dashboard/students" className={linkClass}>
                  <div className="flex items-center gap-3">
                    <Users size={18} />
                    <span>Students</span>
                  </div>
                </NavLink>
                <NavLink to="/dashboard/teachers" className={linkClass}>
                  <div className="flex items-center gap-3">
                    <Users size={18} />
                    <span>Faculty Staff</span>
                  </div>
                </NavLink>
                <NavLink to="/dashboard/users" className={linkClass}>
                  <div className="flex items-center gap-3">
                    <Settings size={18} />
                    <span>Manage Users & RBAC</span>
                  </div>
                </NavLink>
              </div>
            </div>

            {/* Attendance & Analytics */}
            <div>
              <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
                Attendance & Reports
              </p>
              <div className="space-y-1">
                <NavLink to="/dashboard/attendance" className={linkClass}>
                  <div className="flex items-center gap-3">
                    <CalendarCheck size={18} />
                    <span>Attendance Explorer</span>
                  </div>
                </NavLink>
                <NavLink to="/dashboard/reports" className={linkClass}>
                  <div className="flex items-center gap-3">
                    <Activity size={18} />
                    <span>Analytics & Reports</span>
                  </div>
                </NavLink>
              </div>
            </div>
          </>
        )}

        {/* Live Security & Operations */}
        {['hod', 'dean', 'vc', 'admin', 'teacher'].includes(role) && (
          <div>
            <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
              Real-Time Security
            </p>
            <NavLink to="/dashboard/monitoring" className={linkClass}>
              <div className="flex items-center gap-3">
                <Activity size={18} className="text-emerald-500" />
                <span>Live Camera Stream</span>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </NavLink>
          </div>
        )}

        {/* Account Settings */}
        <div>
          <p className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
            Settings
          </p>
          <NavLink to="/dashboard/profile" className={linkClass}>
            <div className="flex items-center gap-3">
              <Settings size={18} />
              <span>User Profile</span>
            </div>
          </NavLink>
        </div>
      </div>

      {/* Bottom Status Widget: Connected Edge Nodes (Matches Image 1 & 4 "Sale Staff Online" style) */}
      <div className="px-4 py-3 bg-slate-50/70 border-t border-slate-100">
        <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>Active Edge Nodes</span>
          <span className="flex items-center gap-1 text-emerald-600 font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
            Live
          </span>
        </p>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700 bg-white p-2 rounded-xl border border-slate-100 shadow-2xs">
            <div className="flex items-center gap-2">
              <div className="relative">
                <div className="w-7 h-7 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center">
                  <Camera size={14} />
                </div>
                <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-white"></span>
              </div>
              <div>
                <p className="font-bold text-[11px] text-slate-900 leading-tight">WEBCAM-01</p>
                <p className="text-[9px] text-slate-400">Lab 1 • LAPTOP-01</p>
              </div>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 font-bold">
              30 FPS
            </span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 py-2 text-rose-600 hover:bg-rose-50 rounded-xl transition-colors mt-3 text-xs font-bold"
        >
          <LogOut size={15} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
    </>
  );
};
