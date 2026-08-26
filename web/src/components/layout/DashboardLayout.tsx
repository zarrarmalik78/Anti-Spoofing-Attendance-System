import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { ChevronRight } from 'lucide-react';

export const DashboardLayout: React.FC = () => {
  const location = useLocation();

  // Generate breadcrumbs from path
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const breadcrumbs = pathSegments.map((segment) => {
    return segment.charAt(0).toUpperCase() + segment.slice(1);
  });

  return (
    <div className="min-h-screen bg-[#F4F6FA] flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col ml-64">
        <Topbar />

        <main className="flex-1 px-8 pt-24 pb-12 overflow-y-auto max-w-7xl w-full mx-auto">
          {/* Dynamic Breadcrumbs (Matching Image 1 & 2 "Dashboards > Message Center" style) */}
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 mb-6">
            <span>Portal</span>
            {breadcrumbs.map((crumb, idx) => (
              <React.Fragment key={idx}>
                <ChevronRight size={12} className="text-slate-300" />
                <span className={idx === breadcrumbs.length - 1 ? 'text-slate-700 font-bold' : 'hover:text-slate-600'}>
                  {crumb}
                </span>
              </React.Fragment>
            ))}
          </div>

          <Outlet />
        </main>
      </div>
    </div>
  );
};
