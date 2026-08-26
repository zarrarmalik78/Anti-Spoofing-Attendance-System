import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/ui/StatCard';
import { SegmentedProgress } from '../../components/ui/SegmentedProgress';
import { DataTable } from '../../components/ui/DataTable';
import type { Column } from '../../components/ui/DataTable';
import { Users, GraduationCap, Building, ShieldCheck, Award } from 'lucide-react';

interface DepartmentOverview {
  id: string;
  name: string;
  code: string;
  head: string;
  studentsCount: number;
  teachersCount: number;
  attendanceRate: number;
  avatars: string[];
}

interface AuditLog {
  id: string;
  userName: string;
  userRole: string;
  action: string;
  time: string;
  node: string;
  status: 'Success' | 'Flagged' | 'Pending';
}

export const GenericAdminDashboard: React.FC = () => {
  const { profile } = useAuth();
  const role = profile?.role || 'admin';

  let title = 'System Administration';
  let subtitle = 'Global University Infrastructure & Real-Time Monitoring';
  let scopeBadge = 'System-Wide Access';

  if (role === 'vc') {
    title = 'Vice Chancellor Overview';
    subtitle = 'Comprehensive Analytics & Governance Across All Faculties';
    scopeBadge = 'University Scope';
  } else if (role === 'dean') {
    title = 'Dean Executive Dashboard';
    subtitle = 'Faculty of Computing & Information Technology Analytics';
    scopeBadge = 'Faculty Scope';
  } else if (role === 'hod') {
    title = 'HOD Department Console';
    subtitle = 'Department of Computer Science Academic Operations';
    scopeBadge = 'Department Scope';
  }

  // Department Cards with Segmented Progress (Image 3 style)
  const departments: DepartmentOverview[] = [
    {
      id: '1',
      name: 'Computer Science',
      code: 'CS',
      head: 'Dr. Kamran Malik',
      studentsCount: 850,
      teachersCount: 42,
      attendanceRate: 89,
      avatars: [
        'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&auto=format&fit=crop&q=80',
      ],
    },
    {
      id: '2',
      name: 'Software Engineering',
      code: 'SE',
      head: 'Dr. Ayesha Siddiqa',
      studentsCount: 620,
      teachersCount: 30,
      attendanceRate: 85,
      avatars: [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=100&auto=format&fit=crop&q=80',
      ],
    },
    {
      id: '3',
      name: 'Data Science & AI',
      code: 'DS',
      head: 'Dr. Bilal Ahmed',
      studentsCount: 480,
      teachersCount: 24,
      attendanceRate: 92,
      avatars: [
        'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=100&auto=format&fit=crop&q=80',
      ],
    },
    {
      id: '4',
      name: 'Cyber Security',
      code: 'CY',
      head: 'Dr. Tariq Mehmood',
      studentsCount: 390,
      teachersCount: 18,
      attendanceRate: 81,
      avatars: [
        'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
      ],
    },
  ];

  // Audit Logs (Image 2 style)
  const auditLogs: AuditLog[] = [
    {
      id: '1',
      userName: 'Dr. Ali Khan',
      userRole: 'Teacher',
      action: 'Verified Attendance Roster (BSCS 6A)',
      time: '10:15 AM',
      node: 'LAPTOP-01',
      status: 'Success',
    },
    {
      id: '2',
      userName: 'Camera Node #1',
      userRole: 'Edge Device',
      action: 'Photo Spoof Blocked (Liveness 0.12)',
      time: '09:42 AM',
      node: 'WEBCAM-01',
      status: 'Flagged',
    },
    {
      id: '3',
      userName: 'Faizan Sheikh',
      userRole: 'Student',
      action: 'Face Check-in Verified (ArcFace 0.96)',
      time: '08:58 AM',
      node: 'WEBCAM-01',
      status: 'Success',
    },
    {
      id: '4',
      userName: 'System Administrator',
      userRole: 'Admin',
      action: 'Synced Firestore Database Entities',
      time: '08:30 AM',
      node: 'Cloud REST',
      status: 'Success',
    },
  ];

  const auditColumns: Column<AuditLog>[] = [
    {
      header: 'Operator / Entity',
      accessor: (row) => (
        <div>
          <p className="font-bold text-slate-800">{row.userName}</p>
          <span className="text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
            {row.userRole}
          </span>
        </div>
      ),
    },
    {
      header: 'Action / Event Log',
      accessor: (row) => <span className="font-medium text-slate-700">{row.action}</span>,
    },
    {
      header: 'Node / Source',
      accessor: (row) => <span className="font-mono text-slate-500 font-semibold">{row.node}</span>,
    },
    {
      header: 'Timestamp',
      accessor: (row) => <span className="text-slate-400 font-medium">{row.time}</span>,
    },
    {
      header: 'Verification Status',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              row.status === 'Success' ? 'bg-emerald-500' : 'bg-rose-500'
            }`}
          ></span>
          <span
            className={`font-bold px-2.5 py-0.5 rounded-full text-[11px] border ${
              row.status === 'Success'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-100'
                : 'bg-rose-50 text-rose-700 border-rose-100'
            }`}
          >
            {row.status}
          </span>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-brand-50 text-brand-600">
            {scopeBadge}
          </span>
          <h2 className="text-2xl font-black text-slate-900 mt-2">{title} 🏛️</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">{subtitle}</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => window.location.assign('/dashboard/monitoring')}
            className="flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm shadow-brand-500/20"
          >
            <ShieldCheck size={16} />
            <span>Open Security Console</span>
          </button>
        </div>
      </div>

      {/* High-Level Stat Cards (Matching Image 4) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Enrolled Students"
          value={role === 'admin' || role === 'vc' ? '12,450' : '2,340'}
          icon={<Users size={20} />}
          trend="+5.4% this semester"
          trendUp={true}
          badge="Verified"
        />
        <StatCard
          title="Faculty Members"
          value={role === 'admin' || role === 'vc' ? '840' : '114'}
          icon={<GraduationCap size={20} />}
          avatars={[
            'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80',
          ]}
          moreAvatarsCount={role === 'admin' ? 837 : 111}
        />
        <StatCard
          title="Active Departments"
          value={role === 'admin' || role === 'vc' ? '24' : '4'}
          icon={<Building size={20} />}
          subtitle="All Operating"
        />
        <StatCard
          title="Campus Attendance"
          value="87.6%"
          icon={<Award size={20} />}
          trend="+2.1% vs last week"
          trendUp={true}
          badge="Healthy"
        />
      </div>

      {/* Department Cards Grid with Segmented Progress (Matching Image 3) */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              {role === 'vc' || role === 'admin' ? 'Faculties & Academic Units' : 'Departmental Breakdown'}
            </h3>
            <p className="text-xs text-slate-400 font-medium">Real-time attendance rates and staff enrollment</p>
          </div>
          <span className="text-xs font-bold text-brand-600 hover:text-brand-700 cursor-pointer">
            View All Units →
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {departments.map((dept) => (
            <div
              key={dept.id}
              className="bg-white rounded-2xl p-5 shadow-soft border border-slate-100 flex flex-col justify-between hover:shadow-soft-lg transition-all"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-brand-50 text-brand-700">
                      {dept.code}
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm mt-2">{dept.name}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{dept.head}</p>
                  </div>
                  {/* Overlapping Avatars (Image 3 style) */}
                  <div className="flex items-center -space-x-2">
                    {dept.avatars.map((img, i) => (
                      <img
                        key={i}
                        src={img}
                        alt="Staff"
                        className="w-6 h-6 rounded-full object-cover ring-2 ring-white"
                      />
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-50 flex items-center justify-between text-xs text-slate-500">
                  <span>{dept.studentsCount} Students</span>
                  <span className="font-bold text-slate-700">{dept.teachersCount} Faculty</span>
                </div>
              </div>

              {/* Segmented Bar (Image 3 style) */}
              <div className="mt-4 pt-3 border-t border-slate-50">
                <div className="flex justify-between items-center text-[11px] font-bold text-slate-500 mb-1.5">
                  <span>Attendance</span>
                  <span className="text-slate-800">{dept.attendanceRate}%</span>
                </div>
                <SegmentedProgress percentage={dept.attendanceRate} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Real-time System Audit Table (Matching Image 2) */}
      <DataTable
        title="Real-Time System Audit & Check-in Logs"
        subtitle="Chronological log of Edge AI attendance events, spoof blocks, and cloud synchronization"
        data={auditLogs}
        columns={auditColumns}
        searchPlaceholder="Search operator, event or node..."
        onExport={() => alert('Exporting Audit Logs CSV...')}
      />
    </div>
  );
};
