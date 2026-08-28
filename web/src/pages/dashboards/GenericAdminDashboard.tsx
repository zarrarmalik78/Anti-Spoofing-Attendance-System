import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/ui/StatCard';
import { SegmentedProgress } from '../../components/ui/SegmentedProgress';
import { DataTable } from '../../components/ui/DataTable';
import type { Column } from '../../components/ui/DataTable';
import { Users, GraduationCap, Building, ShieldCheck, Award } from 'lucide-react';
import { collection, getDocs, query, orderBy, limit } from 'firebase/firestore';
import { db } from '../../firebase/config';

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

  const [loading, setLoading] = useState(true);
  const [departments, setDepartments] = useState<DepartmentOverview[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [metrics, setMetrics] = useState({
    totalStudents: 0,
    totalTeachers: 0,
    activeUnits: 0,
    campusAttendance: 0,
  });

  let title = 'System Administration';
  let subtitle = 'Global University Infrastructure & Real-Time Monitoring';
  let scopeBadge = 'System-Wide Access';

  if (role === 'vc') {
    title = 'Vice Chancellor Overview';
    subtitle = 'Comprehensive Analytics & Governance Across All Faculties';
    scopeBadge = 'University Scope';
  } else if (role === 'dean') {
    title = 'Dean Executive Dashboard';
    subtitle = 'Faculty Academic Performance & Staff Telemetry';
    scopeBadge = 'Faculty Scope';
  } else if (role === 'hod') {
    title = 'HOD Department Console';
    subtitle = 'Department Academic Operations & Student Verification';
    scopeBadge = 'Department Scope';
  }

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // 1. Fetch Departments
        const deptsSnap = await getDocs(collection(db, 'departments'));
        let deptsData = deptsSnap.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as any[];

        // 2. Fetch Teachers
        const teachersSnap = await getDocs(collection(db, 'teachers'));
        let teachersData = teachersSnap.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as any[];

        // 3. Fetch Students
        const studentsSnap = await getDocs(collection(db, 'students'));
        let studentsData = studentsSnap.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as any[];

        // 4. Fetch Attendance for calculations
        const attSnap = await getDocs(query(collection(db, 'attendance'), limit(2000)));
        const attData = attSnap.docs.map((doc) => doc.data()) as any[];

        // 5. Fetch Recognition Events for Audit Logs
        const eventsSnap = await getDocs(
          query(collection(db, 'recognition_events'), orderBy('timestamp', 'desc'), limit(15))
        );
        const eventsData = eventsSnap.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        })) as any[];

        // Apply RBAC Scoping
        if (role === 'dean' && profile?.scope?.facultyId) {
          deptsData = deptsData.filter((d) => d.facultyId === profile.scope.facultyId);
          const deptIds = new Set(deptsData.map((d) => d.id));
          teachersData = teachersData.filter((t) => deptIds.has(t.departmentId));
          studentsData = studentsData.filter((s) => deptIds.has(s.departmentId));
        } else if (role === 'hod' && profile?.scope?.departmentId) {
          deptsData = deptsData.filter((d) => d.id === profile.scope.departmentId);
          teachersData = teachersData.filter((t) => t.departmentId === profile.scope.departmentId);
          studentsData = studentsData.filter((s) => s.departmentId === profile.scope.departmentId);
        }

        // Calculate Department level breakdown
        const deptsOverview: DepartmentOverview[] = deptsData.map((dept) => {
          const deptStudents = studentsData.filter((s) => s.departmentId === dept.id);
          const deptTeachers = teachersData.filter((t) => t.departmentId === dept.id);
          const deptAtt = attData.filter((a) => a.departmentId === dept.id);

          const presentCount = deptAtt.filter((a) => a.status === 'Present' || a.status === 'Late').length;
          const rate = deptAtt.length > 0 ? Math.round((presentCount / deptAtt.length) * 100) : 88;

          const avatars = deptTeachers.slice(0, 3).map((t) => t.avatar).filter(Boolean);
          if (avatars.length === 0) {
            avatars.push('https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80');
          }

          return {
            id: dept.id,
            name: dept.name,
            code: dept.code || dept.name.substring(0, 2).toUpperCase(),
            head: dept.head || 'Department Chair',
            studentsCount: deptStudents.length,
            teachersCount: deptTeachers.length,
            attendanceRate: rate,
            avatars: avatars,
          };
        });

        // Compute High-Level Metrics
        const totalPresent = attData.filter((a) => a.status === 'Present' || a.status === 'Late').length;
        const overallRate = attData.length > 0 ? Math.round((totalPresent / attData.length) * 1000) / 10 : 86.4;

        setMetrics({
          totalStudents: studentsData.length,
          totalTeachers: teachersData.length,
          activeUnits: deptsData.length,
          campusAttendance: overallRate,
        });

        setDepartments(deptsOverview);

        // Map events to Audit Logs Table
        const mappedLogs: AuditLog[] = eventsData.map((evt) => {
          let act = 'Face Check-in Verified';
          let st: 'Success' | 'Flagged' | 'Pending' = 'Success';
          let roleName = 'Student';

          if (evt.eventType === 'SPOOF') {
            act = `Spoof Attack Blocked (Liveness ${(evt.livenessScore * 100).toFixed(0)}%)`;
            st = 'Flagged';
            roleName = 'Intruder';
          } else if (evt.eventType === 'UNKNOWN') {
            act = 'Unregistered Person Detected';
            st = 'Pending';
            roleName = 'Visitor';
          } else {
            act = `Face Verified (Confidence ${(evt.confidence * 100).toFixed(0)}%)`;
          }

          const dateObj = evt.timestamp ? new Date(evt.timestamp * 1000) : new Date();
          const timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          return {
            id: evt.id,
            userName: evt.studentName || 'Unregistered Person',
            userRole: roleName,
            action: act,
            time: timeStr,
            node: evt.cameraId || 'WEBCAM-01',
            status: st,
          };
        });

        setAuditLogs(mappedLogs);
      } catch (err) {
        console.error('Failed to fetch admin dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [profile, role]);

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
              row.status === 'Success'
                ? 'bg-emerald-500'
                : row.status === 'Flagged'
                ? 'bg-rose-500'
                : 'bg-amber-500'
            }`}
          ></span>
          <span
            className={`font-bold px-2.5 py-0.5 rounded-full text-[11px] border ${
              row.status === 'Success'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-100'
                : row.status === 'Flagged'
                ? 'bg-rose-50 text-rose-700 border-rose-100'
                : 'bg-amber-50 text-amber-700 border-amber-100'
            }`}
          >
            {row.status}
          </span>
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex justify-center p-16">
        <div className="animate-spin rounded-full h-9 w-9 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-brand-950 to-indigo-950 rounded-3xl p-7 text-white shadow-soft-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-5 relative overflow-hidden border border-slate-800">
        <div className="relative z-10">
          <span className="px-3 py-1 bg-white/10 rounded-full text-xs font-bold uppercase tracking-wider backdrop-blur-sm border border-white/10 text-brand-300">
            {scopeBadge}
          </span>
          <h2 className="text-2xl font-black mt-3 text-white tracking-tight">{title} 🏛️</h2>
          <p className="text-slate-300 text-xs font-medium mt-1">{subtitle}</p>
        </div>

        <div className="flex items-center gap-3 relative z-10">
          <button
            onClick={() => window.location.assign('/dashboard/monitoring')}
            className="flex items-center gap-2 px-5 py-3 bg-brand-600 hover:bg-brand-500 text-white rounded-2xl text-xs font-extrabold transition-all shadow-lg shadow-brand-600/30 hover:scale-[1.02] active:scale-95"
          >
            <ShieldCheck size={16} />
            <span>Open Security Console</span>
          </button>
        </div>
      </div>

      {/* High-Level Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Enrolled Students"
          value={metrics.totalStudents.toLocaleString()}
          icon={<Users size={20} />}
          trend="+5.4% this semester"
          trendUp={true}
          badge="Verified"
        />
        <StatCard
          title="Faculty Members"
          value={metrics.totalTeachers.toLocaleString()}
          icon={<GraduationCap size={20} />}
          avatars={[
            'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80',
          ]}
          moreAvatarsCount={Math.max(0, metrics.totalTeachers - 3)}
        />
        <StatCard
          title="Active Departments"
          value={metrics.activeUnits.toString()}
          icon={<Building size={20} />}
          subtitle="All Operational"
        />
        <StatCard
          title="Campus Attendance"
          value={`${metrics.campusAttendance}%`}
          icon={<Award size={20} />}
          trend="+2.1% vs last week"
          trendUp={true}
          badge="Healthy"
        />
      </div>

      {/* Department Cards Grid with Segmented Progress */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              {role === 'vc' || role === 'admin' ? 'Faculties & Academic Units' : 'Departmental Breakdown'}
            </h3>
            <p className="text-xs text-slate-400 font-medium">Real-time attendance rates and staff enrollment</p>
          </div>
          <span className="text-xs font-bold text-brand-600 hover:text-brand-700 cursor-pointer">
            {departments.length} Units Active →
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

      {/* Real-time System Audit Table */}
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
