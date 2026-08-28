import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebase/config';
import { useAuth } from '../context/AuthContext';
import { Sparkles, Lock, Mail, ArrowRight } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { user, profile } = useAuth();

  // If already logged in and profile is loaded, redirect to dashboard
  if (user && profile) {
    return <Navigate to={`/dashboard/${profile.role}`} replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.');
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('password123');
  };

  return (
    <div className="min-h-screen bg-[#F4F6FA] flex items-center justify-center p-4 sm:p-6 lg:p-10 relative overflow-hidden font-sans">
      {/* Background Soft Glow Spots */}
      <div className="absolute top-0 left-1/4 w-[600px] h-[300px] bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[300px] bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-5xl w-full bg-white rounded-3xl shadow-2xl border border-slate-100/90 overflow-hidden grid grid-cols-1 lg:grid-cols-12 relative z-10">
        
        {/* Left Column: Login Form */}
        <div className="lg:col-span-6 p-8 sm:p-10 lg:p-12 flex flex-col justify-between">
          <div>
            {/* Logo & Brand Header */}
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white flex items-center justify-center shadow-md shadow-brand-500/20">
                <Sparkles size={20} className="animate-pulse" />
              </div>
              <div>
                <h1 className="text-lg font-black text-slate-900 tracking-tight flex items-center gap-1.5">
                  Edge AI <span className="text-[10px] uppercase font-extrabold px-1.5 py-0.5 rounded bg-brand-100 text-brand-700">OS</span>
                </h1>
                <p className="text-[11px] font-medium text-slate-400">Attendance & Security Portal</p>
              </div>
            </div>

            {/* Headline */}
            <div className="mb-6">
              <h2 className="text-3xl font-black text-slate-900 tracking-tight">Welcome Back !</h2>
              <p className="text-xs text-slate-400 font-medium mt-1">Please enter your university credentials</p>
            </div>

            {/* Form */}
            <form className="space-y-4" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-rose-50 border border-rose-100 text-rose-600 px-4 py-3 rounded-2xl text-xs font-semibold">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    required
                    placeholder="name@university.edu"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200/80 rounded-2xl text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
                  />
                  <Mail size={16} className="absolute left-3.5 top-3.5 text-slate-400 pointer-events-none" />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="block text-xs font-bold text-slate-700">
                    Password
                  </label>
                  <a href="#forgot" onClick={(e) => { e.preventDefault(); alert('Please contact University IT Admin to reset password.'); }} className="text-[11px] font-bold text-brand-600 hover:text-brand-700">
                    Forgot Password?
                  </a>
                </div>
                <div className="relative">
                  <input
                    type="password"
                    required
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200/80 rounded-2xl text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
                  />
                  <Lock size={16} className="absolute left-3.5 top-3.5 text-slate-400 pointer-events-none" />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="remember"
                  defaultChecked
                  className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
                />
                <label htmlFor="remember" className="text-xs font-medium text-slate-600">
                  Remember me on this device
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3.5 px-4 bg-brand-600 hover:bg-brand-700 active:scale-[0.99] text-white rounded-2xl text-xs font-bold transition-all shadow-lg shadow-brand-500/25 disabled:opacity-60 mt-2"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Login</span>
                    <ArrowRight size={15} />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Quick Login Test Accounts */}
          <div className="mt-8 pt-6 border-t border-slate-100">
            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2.5">
              ⚡ Demo Accounts
            </p>
            <div className="grid grid-cols-3 gap-1.5">
              <button
                type="button"
                onClick={() => handleQuickLogin('admin@university.edu')}
                className="py-1.5 px-2 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-700 text-[10px] font-extrabold transition-colors text-center"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('vc@university.edu')}
                className="py-1.5 px-2 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-800 text-[10px] font-extrabold transition-colors text-center"
              >
                VC
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('dean@university.edu')}
                className="py-1.5 px-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-800 text-[10px] font-extrabold transition-colors text-center"
              >
                Dean
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('hod@university.edu')}
                className="py-1.5 px-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-800 text-[10px] font-extrabold transition-colors text-center"
              >
                HOD
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('ali.khan@university.edu')}
                className="py-1.5 px-2 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-[10px] font-extrabold transition-colors text-center"
              >
                Teacher
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('zarar@university.edu')}
                className="py-1.5 px-2 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 text-[10px] font-extrabold transition-colors text-center"
              >
                Zarar
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Beautiful Banner Card with Generated AI Illustration */}
        <div className="lg:col-span-6 bg-gradient-to-br from-brand-600 via-indigo-600 to-purple-700 p-8 sm:p-10 flex flex-col justify-between relative text-white overflow-hidden m-2 rounded-3xl">
          {/* Subtle Ambient Mesh overlay */}
          <div className="absolute -right-20 -top-20 w-80 h-80 bg-white/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -left-20 -bottom-20 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />

          {/* Top Pill */}
          <div className="flex items-center justify-between relative z-10 mb-6">
            <span className="px-3.5 py-1.5 bg-white/15 backdrop-blur-md rounded-full text-[11px] font-extrabold uppercase tracking-wider text-white border border-white/20">
              Edge Biometrics OS
            </span>
          </div>

          {/* Illustration Container Card */}
          <div className="relative z-10 my-auto flex flex-col items-center">
            <div className="w-full max-w-sm bg-white/10 backdrop-blur-md p-3.5 rounded-3xl border border-white/20 shadow-2xl overflow-hidden group">
              <img
                src="/edge_ai_illustration.jpg"
                alt="Edge AI Biometric Illustration"
                className="w-full h-auto rounded-2xl object-cover shadow-lg group-hover:scale-105 transition-transform duration-500"
              />
            </div>
          </div>

          {/* Bottom Headline & Tagline */}
          <div className="relative z-10 mt-6 text-center">
            <h3 className="text-2xl font-black text-white tracking-tight">Seamless Biometric Experience</h3>
            <p className="text-brand-100 text-xs font-semibold mt-1">
              Real-time facial recognition attendance, anti-spoofing guard & university AI analytics.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};
