import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Bell, User } from 'lucide-react';

export const Topbar: React.FC = () => {
  const { profile } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 fixed top-0 right-0 left-64 z-10">
      <div className="flex-1">
        {/* Breadcrumbs could go here */}
        <h2 className="text-xl font-semibold text-gray-800 capitalize">
          {profile?.role} Portal
        </h2>
      </div>
      
      <div className="flex items-center space-x-4">
        <button className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100">
          <Bell size={20} />
        </button>
        
        <div className="flex items-center space-x-3 border-l border-gray-200 pl-4">
          <div className="text-right hidden md:block">
            <p className="text-sm font-medium text-gray-900">{profile?.name}</p>
            <p className="text-xs text-gray-500 capitalize">{profile?.role}</p>
          </div>
          <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold">
            {profile?.name?.charAt(0) || <User size={16} />}
          </div>
        </div>
      </div>
    </header>
  );
};
