import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Bell, Search, Calendar, User, LogOut, Shield, Menu } from 'lucide-react';
import { NotificationPopover } from '../ui/NotificationPopover';
import { auth } from '../../firebase/config';
import { useNavigate } from 'react-router-dom';

interface TopbarProps {
  onToggleMobileMenu?: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onToggleMobileMenu }) => {
  const { profile } = useAuth();
  const navigate = useNavigate();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const currentDate = new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric',
  }).format(new Date());

  const getRoleBadgeColor = (role?: string) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-700';
      case 'vc':
        return 'bg-amber-100 text-amber-800';
      case 'dean':
        return 'bg-blue-100 text-blue-800';
      case 'hod':
        return 'bg-indigo-100 text-indigo-800';
      case 'teacher':
        return 'bg-emerald-100 text-emerald-800';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/dashboard/attendance?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = () => {
    auth.signOut();
  };

  return (
    <header className="h-18 bg-white/90 backdrop-blur-md border-b border-slate-100 flex items-center justify-between px-4 sm:px-8 fixed top-0 right-0 left-0 lg:left-64 z-30 transition-all duration-200">
      {/* Left: Mobile Menu Toggle & Date pill badge */}
      <div className="flex items-center gap-3">
        {onToggleMobileMenu && (
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors"
            aria-label="Toggle navigation menu"
          >
            <Menu size={20} />
          </button>
        )}

        <div className="hidden xs:flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200/70 text-slate-700 text-xs font-bold shadow-2xs">
          <span>{currentDate}</span>
          <Calendar size={14} className="text-brand-600" />
        </div>
      </div>

      {/* Center/Right Actions */}
      <div className="flex items-center gap-4">
        {/* Search Bar Form */}
        <form onSubmit={handleSearchSubmit} className="relative hidden md:block w-64 lg:w-80">
          <input
            type="text"
            placeholder="Search students, classes, logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-4 pr-10 py-2 bg-slate-50 border border-slate-200/80 rounded-full text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
          />
          <button type="submit" className="absolute right-3.5 top-2.5 text-slate-400 hover:text-brand-600">
            <Search size={15} />
          </button>
        </form>

        {/* Action Buttons with Notification Popover */}
        <div className="flex items-center gap-2 relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowProfileMenu(false);
            }}
            className="relative p-2.5 text-slate-400 hover:text-brand-600 hover:bg-slate-50 rounded-full transition-all"
            aria-label="View notifications"
          >
            <Bell size={18} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white animate-ping"></span>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white"></span>
          </button>

          <NotificationPopover
            isOpen={showNotifications}
            onClose={() => setShowNotifications(false)}
          />
        </div>

        {/* User Profile Dropdown Button */}
        <div className="relative pl-3 border-l border-slate-100">
          <button
            onClick={() => {
              setShowProfileMenu(!showProfileMenu);
              setShowNotifications(false);
            }}
            className="flex items-center gap-3 hover:bg-slate-50 p-1.5 rounded-2xl transition-all"
          >
            <div className="text-right hidden sm:block">
              <p className="text-xs font-bold text-slate-900 leading-tight">{profile?.name || 'User'}</p>
              <span
                className={`inline-block text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full mt-0.5 ${getRoleBadgeColor(
                  profile?.role
                )}`}
              >
                {profile?.role || 'Guest'}
              </span>
            </div>

            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-brand-600 to-indigo-400 text-white flex items-center justify-center font-black text-sm shadow-md shadow-brand-500/20 ring-2 ring-white">
                {profile?.name?.charAt(0) || 'U'}
              </div>
              <span className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-white"></span>
            </div>
          </button>

          {/* Profile Dropdown Menu */}
          {showProfileMenu && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setShowProfileMenu(false)} />
              <div className="absolute right-0 top-14 w-64 bg-white rounded-2xl shadow-2xl border border-slate-100 z-50 p-3 space-y-2 animate-fade-in">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                  <p className="font-bold text-slate-900 text-xs">{profile?.name || 'User'}</p>
                  <p className="text-[11px] text-slate-400 truncate mt-0.5">{profile?.email}</p>
                  <span className="inline-block mt-2 text-[10px] font-extrabold px-2 py-0.5 bg-brand-50 text-brand-700 rounded-md">
                    Scope: {profile?.role?.toUpperCase()}
                  </span>
                </div>

                <div className="space-y-1 text-xs font-semibold">
                  <button
                    onClick={() => {
                      setShowProfileMenu(false);
                      navigate(`/dashboard/${profile?.role || 'student'}`);
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 flex items-center gap-2.5"
                  >
                    <User size={14} className="text-brand-600" />
                    <span>My Dashboard</span>
                  </button>

                  <button
                    onClick={() => {
                      setShowProfileMenu(false);
                      navigate('/dashboard/users');
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 flex items-center gap-2.5"
                  >
                    <Shield size={14} className="text-brand-600" />
                    <span>User Roster & Scope</span>
                  </button>
                </div>

                <div className="pt-2 border-t border-slate-100">
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 rounded-xl text-rose-600 hover:bg-rose-50 flex items-center gap-2.5 text-xs font-bold transition-colors"
                  >
                    <LogOut size={14} />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
