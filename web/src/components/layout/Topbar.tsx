import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Bell, Search, Calendar } from 'lucide-react';
import { NotificationPopover } from '../ui/NotificationPopover';

export const Topbar: React.FC = () => {
  const { profile } = useAuth();
  const [showNotifications, setShowNotifications] = useState(false);
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

  return (
    <header className="h-18 bg-white/90 backdrop-blur-md border-b border-slate-100 flex items-center justify-between px-8 fixed top-0 right-0 left-64 z-20 transition-all duration-200">
      {/* Left: Date pill badge (Matching Image 1 & 4 "March 2024 📅" style) */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200/70 text-slate-700 text-xs font-bold shadow-2xs">
          <span>{currentDate}</span>
          <Calendar size={14} className="text-brand-600" />
        </div>
      </div>

      {/* Center/Right Actions */}
      <div className="flex items-center gap-4">
        {/* Search Bar Pill (Matching Image 1, 2, 4) */}
        <div className="relative hidden md:block w-64 lg:w-80">
          <input
            type="text"
            placeholder="Search students, classes, logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-4 pr-10 py-2 bg-slate-50 border border-slate-200/80 rounded-full text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
          />
          <Search size={15} className="absolute right-3.5 top-2.5 text-slate-400 pointer-events-none" />
        </div>

        {/* Action Buttons with Notification Popover */}
        <div className="flex items-center gap-2 relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2.5 text-slate-400 hover:text-brand-600 hover:bg-slate-50 rounded-full transition-all"
            aria-label="View notifications"
          >
            <Bell size={18} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white"></span>
          </button>

          <NotificationPopover
            isOpen={showNotifications}
            onClose={() => setShowNotifications(false)}
          />
        </div>

        {/* User Profile Chip (Matching Image 1 & 4) */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-100">
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
        </div>
      </div>
    </header>
  );
};
