import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/ui/StatCard';
import { Users, GraduationCap, Building, BookOpen } from 'lucide-react';

export const GenericAdminDashboard: React.FC = () => {
  const { profile } = useAuth();
  
  const role = profile?.role || 'admin';
  
  let title = "Admin Overview";
  let scope = "System-wide";
  
  if (role === 'vc') {
    title = "Vice Chancellor Dashboard";
    scope = "University-wide";
  } else if (role === 'dean') {
    title = "Dean Dashboard";
    scope = "Faculty Level";
  } else if (role === 'hod') {
    title = "HOD Dashboard";
    scope = "Department Level";
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <p className="text-gray-500 mt-1">{scope} Statistics</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Students" value={role === 'admin' || role === 'vc' ? 12450 : 850} icon={<Users />} />
        <StatCard title="Total Teachers" value={role === 'admin' || role === 'vc' ? 840 : 45} icon={<GraduationCap />} />
        {role !== 'hod' && <StatCard title="Departments" value={role === 'admin' || role === 'vc' ? 24 : 6} icon={<Building />} />}
        <StatCard title="Active Courses" value={role === 'admin' || role === 'vc' ? 450 : 28} icon={<BookOpen />} />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mt-8">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Attendance Overview</h3>
        </div>
        <div className="p-12 text-center text-gray-500">
          <div className="mx-auto h-48 w-full max-w-lg bg-gray-50 rounded-lg flex items-center justify-center border border-dashed border-gray-300">
            [ Attendance Chart Placeholder ]
          </div>
        </div>
      </div>
    </div>
  );
};
