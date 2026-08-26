import React, { useState } from 'react';
import { ShieldAlert, X, Bell } from 'lucide-react';
import { NavLink } from 'react-router-dom';

interface NotificationItem {
  id: string;
  title: string;
  subtitle: string;
  time: string;
  type: 'spoof' | 'recognized' | 'system';
  avatar?: string;
}

interface NotificationPopoverProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationPopover: React.FC<NotificationPopoverProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'alerts' | 'activity'>('alerts');

  if (!isOpen) return null;

  const notifications: NotificationItem[] = [
    {
      id: '1',
      title: 'Anti-Spoofing Alert',
      subtitle: 'Photo spoof attempt blocked on WEBCAM-01 (Liveness: 14%)',
      time: '08:30 AM',
      type: 'spoof',
    },
    {
      id: '2',
      title: 'Student Verified',
      subtitle: 'Ali Khan checked in for BSCS 6A - Artificial Intelligence',
      time: '08:28 AM',
      type: 'recognized',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
    },
    {
      id: '3',
      title: 'Edge Node Sync',
      subtitle: 'LAPTOP-01 synced 15 attendance records to Cloud Firestore',
      time: '08:15 AM',
      type: 'system',
    },
    {
      id: '4',
      title: 'Student Verified',
      subtitle: 'Sara Ahmed checked in for BSCS 6A - Web Engineering',
      time: '08:04 AM',
      type: 'recognized',
      avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80',
    },
  ];

  return (
    <>
      <div className="fixed inset-0 z-40" onClick={onClose} />
      <div className="absolute right-0 top-14 w-96 bg-white rounded-2xl shadow-2xl border border-slate-100 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-slate-900 text-base">Live Activity & Alerts</h3>
            <span className="bg-brand-50 text-brand-600 text-xs px-2 py-0.5 rounded-full font-bold">
              4 New
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex border-b border-slate-100 px-4 pt-2 gap-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('alerts')}
            className={`pb-2 border-b-2 transition-colors ${
              activeTab === 'alerts'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-400 hover:text-slate-600'
            }`}
          >
            Security Alerts
          </button>
          <button
            onClick={() => setActiveTab('activity')}
            className={`pb-2 border-b-2 transition-colors ${
              activeTab === 'activity'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-400 hover:text-slate-600'
            }`}
          >
            Live Check-ins
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto divide-y divide-slate-50 p-2">
          {notifications.map((item) => (
            <div
              key={item.id}
              className="p-3 hover:bg-slate-50 rounded-xl transition-colors flex items-start gap-3 cursor-pointer"
            >
              {item.avatar ? (
                <img
                  src={item.avatar}
                  alt={item.title}
                  className="w-10 h-10 rounded-full object-cover shrink-0 ring-2 ring-slate-100"
                />
              ) : item.type === 'spoof' ? (
                <div className="w-10 h-10 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                  <ShieldAlert size={20} />
                </div>
              ) : (
                <div className="w-10 h-10 rounded-full bg-brand-50 text-brand-600 flex items-center justify-center shrink-0">
                  <Bell size={20} />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1">
                  <h4 className="text-xs font-bold text-slate-900 truncate">{item.title}</h4>
                  <span className="text-[10px] text-slate-400 shrink-0">{item.time}</span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5 leading-relaxed line-clamp-2">
                  {item.subtitle}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="p-3 bg-slate-50/70 border-t border-slate-100 text-center">
          <NavLink
            to="/dashboard/monitoring"
            onClick={onClose}
            className="block w-full py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm shadow-brand-500/20"
          >
            Open Live Security Console
          </NavLink>
        </div>
      </div>
    </>
  );
};
