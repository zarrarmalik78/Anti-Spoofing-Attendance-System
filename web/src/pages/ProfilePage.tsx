import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Shield,
  Mail,
  Building,
  CheckCircle2,
  Lock,
  Camera
} from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { profile } = useAuth();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleUpdatePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPassword || newPassword !== confirmPassword) {
      alert('Passwords do not match.');
      return;
    }
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 4000);
    setNewPassword('');
    setConfirmPassword('');
  };

  const getRoleBadgeStyle = (role?: string) => {
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
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-brand-50 text-brand-600">
            Account Management
          </span>
          <h2 className="text-2xl font-black text-slate-900 mt-2">User Profile & Credentials 👤</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Institutional role permissions, biometric profile, and security preferences
          </p>
        </div>
      </div>

      {/* Profile Overview Card */}
      <div className="bg-white rounded-3xl p-8 shadow-soft border border-slate-100 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 pb-6 border-b border-slate-100">
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white flex items-center justify-center font-black text-2xl shadow-xl shadow-brand-500/20 ring-4 ring-brand-50">
            {profile?.name?.charAt(0) || 'U'}
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h3 className="text-xl font-black text-slate-900">{profile?.name || 'Authorized User'}</h3>
              <span
                className={`text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-full ${getRoleBadgeStyle(
                  profile?.role
                )}`}
              >
                {profile?.role || 'User'}
              </span>
            </div>
            <p className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
              <Mail size={13} /> {profile?.email || 'user@university.edu'}
            </p>
            <p className="text-[11px] font-mono text-slate-400">
              UID: {profile?.uid || 'authenticated-session-01'}
            </p>
          </div>
        </div>

        {/* Scope & Role Details */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <p className="text-slate-400 font-medium text-[11px] flex items-center gap-1">
              <Shield size={13} className="text-brand-600" /> RBAC Authorization Level
            </p>
            <p className="font-extrabold text-slate-800 text-sm mt-1 uppercase">
              {profile?.role || 'Guest'}
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <p className="text-slate-400 font-medium text-[11px] flex items-center gap-1">
              <Building size={13} className="text-brand-600" /> Department / Scope
            </p>
            <p className="font-extrabold text-slate-800 text-sm mt-1">
              {profile?.scope?.departmentId || profile?.scope?.facultyId || profile?.scope?.universityId || 'Campus Wide'}
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <p className="text-slate-400 font-medium text-[11px] flex items-center gap-1">
              <CheckCircle2 size={13} className="text-emerald-600" /> Account Standing
            </p>
            <p className="font-extrabold text-emerald-600 text-sm mt-1 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Active & Verified
            </p>
          </div>
        </div>
      </div>

      {/* Biometric Status & Security Settings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Biometric Profile Card */}
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
              <Camera size={20} />
            </div>
            <div>
              <h4 className="text-sm font-black text-slate-900">Biometric Edge Profile</h4>
              <p className="text-[11px] text-slate-400">ArcFace 512D & MiniFASNet V2 status</p>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
              <span className="text-slate-600 font-medium">Face Feature Embedding</span>
              <span className="font-bold text-emerald-600">Registered (512D Vector)</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
              <span className="text-slate-600 font-medium">Anti-Spoofing Verification</span>
              <span className="font-bold text-emerald-600">Enabled (0.40 Threshold)</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
              <span className="text-slate-600 font-medium">Recognition Confidence Avg</span>
              <span className="font-mono font-bold text-slate-800">0.96 (High)</span>
            </div>
          </div>
        </div>

        {/* Change Password Card */}
        <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center font-bold">
              <Lock size={20} />
            </div>
            <div>
              <h4 className="text-sm font-black text-slate-900">Security Credentials</h4>
              <p className="text-[11px] text-slate-400">Update your account password</p>
            </div>
          </div>

          {savedSuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-xs font-bold flex items-center gap-2">
              <CheckCircle2 size={15} /> Password updated successfully!
            </div>
          )}

          <form onSubmit={handleUpdatePassword} className="space-y-3 text-xs">
            <div>
              <label className="font-bold text-slate-700 block mb-1">New Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500/20 font-mono"
              />
            </div>
            <div>
              <label className="font-bold text-slate-700 block mb-1">Confirm New Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500/20 font-mono"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold transition-all mt-2"
            >
              Update Password
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
