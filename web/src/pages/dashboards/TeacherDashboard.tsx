import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/ui/StatCard';
import { SegmentedProgress } from '../../components/ui/SegmentedProgress';
import { DataTable } from '../../components/ui/DataTable';
import type { Column } from '../../components/ui/DataTable';
import { Users, BookOpen, UserCheck, Percent, Plus } from 'lucide-react';

interface StudentRoster {
  id: string;
  name: string;
  rollNumber: string;
  email: string;
  attendancePercent: number;
  lastCheckIn: string;
  status: 'Present' | 'Absent' | 'Late';
  avatar: string;
}

export const TeacherDashboard: React.FC = () => {
  const { profile } = useAuth();
  const [selectedClass, setSelectedClass] = useState<string>('class-ai-6a');

  // Assigned classes (Image 3 style)
  const assignedClasses = [
    {
      id: 'class-ai-6a',
      courseCode: 'CS401',
      courseName: 'Artificial Intelligence',
      section: 'BSCS 6A',
      room: 'Lab 1',
      time: 'Mon / Wed 10:00 AM',
      studentsCount: 45,
      attendanceRate: 88,
      avatars: [
        'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&auto=format&fit=crop&q=80',
      ],
    },
    {
      id: 'class-web-6a',
      courseCode: 'CS402',
      courseName: 'Web Engineering',
      section: 'BSCS 6A',
      room: 'Lab 2',
      time: 'Tue / Thu 11:30 AM',
      studentsCount: 42,
      attendanceRate: 82,
      avatars: [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=100&auto=format&fit=crop&q=80',
      ],
    },
    {
      id: 'class-ai-6b',
      courseCode: 'CS401',
      courseName: 'Artificial Intelligence',
      section: 'BSCS 6B',
      room: 'Hall B',
      time: 'Mon / Wed 02:00 PM',
      studentsCount: 38,
      attendanceRate: 91,
      avatars: [
        'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=100&auto=format&fit=crop&q=80',
      ],
    },
  ];

  // Student roster for selected class (Image 2 style)
  const studentsList: StudentRoster[] = [
    {
      id: '1',
      name: 'Darrell Steward',
      rollNumber: 'FA23-BCS-001',
      email: 'darrell@university.edu',
      attendancePercent: 92,
      lastCheckIn: 'Today, 10:02 AM',
      status: 'Present',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
    },
    {
      id: '2',
      name: 'Jenny Wilson',
      rollNumber: 'FA23-BCS-002',
      email: 'jenny.w@university.edu',
      attendancePercent: 84,
      lastCheckIn: 'Today, 10:04 AM',
      status: 'Present',
      avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80',
    },
    {
      id: '3',
      name: 'Kathryn Murphy',
      rollNumber: 'FA23-BCS-003',
      email: 'kmurphy@university.edu',
      attendancePercent: 65,
      lastCheckIn: 'Yesterday, 11:32 AM',
      status: 'Absent',
      avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&auto=format&fit=crop&q=80',
    },
    {
      id: '4',
      name: 'Robert Fox',
      rollNumber: 'FA23-BCS-004',
      email: 'robert.f@university.edu',
      attendancePercent: 95,
      lastCheckIn: 'Today, 10:01 AM',
      status: 'Present',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
    },
    {
      id: '5',
      name: 'Yuni Nadia',
      rollNumber: 'FA23-BCS-005',
      email: 'yuni.n@university.edu',
      attendancePercent: 78,
      lastCheckIn: 'Today, 10:14 AM',
      status: 'Late',
      avatar: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=100&auto=format&fit=crop&q=80',
    },
  ];

  // Weekly attendance bar chart data (Image 4 style)
  const attendanceTrend = [
    { day: '11 Mar', height: 85, active: false },
    { day: '12 Mar', height: 92, active: false },
    { day: '13 Mar', height: 78, active: false },
    { day: '14 Mar', height: 96, active: true, tooltip: '96% Present' },
    { day: '15 Mar', height: 88, active: false },
    { day: '16 Mar', height: 90, active: false },
    { day: '17 Mar', height: 84, active: false },
  ];

  const columns: Column<StudentRoster>[] = [
    {
      header: 'Student Name',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <img src={row.avatar} alt={row.name} className="w-8 h-8 rounded-full object-cover ring-2 ring-slate-100" />
          <div>
            <p className="font-bold text-slate-800">{row.name}</p>
            <p className="text-[11px] text-slate-400">{row.email}</p>
          </div>
        </div>
      ),
    },
    {
      header: 'Roll Number',
      accessor: (row) => <span className="font-mono text-slate-600 font-semibold">{row.rollNumber}</span>,
    },
    {
      header: 'Overall Attendance',
      accessor: (row) => (
        <div className="w-36">
          <SegmentedProgress
            percentage={row.attendancePercent}
            variant={row.attendancePercent >= 80 ? 'success' : row.attendancePercent >= 70 ? 'warning' : 'danger'}
          />
        </div>
      ),
    },
    {
      header: 'Last Detected',
      accessor: (row) => <span className="text-slate-600 font-medium">{row.lastCheckIn}</span>,
    },
    {
      header: 'Today Status',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              row.status === 'Present' ? 'bg-emerald-500' : row.status === 'Late' ? 'bg-amber-500' : 'bg-rose-500'
            }`}
          ></span>
          <span
            className={`font-bold px-2.5 py-0.5 rounded-full text-[11px] border ${
              row.status === 'Present'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-100'
                : row.status === 'Late'
                ? 'bg-amber-50 text-amber-700 border-amber-100'
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
      {/* Top Header Card */}
      <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-brand-50 text-brand-600">
            Instructor Portal
          </span>
          <h2 className="text-2xl font-black text-slate-900 mt-2">Welcome, {profile?.name || 'Dr. Ali Khan'} 👨‍🏫</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Faculty of Computing • Department of Computer Science
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm shadow-brand-500/20">
            <Plus size={16} />
            <span>Mark Manual Exception</span>
          </button>
        </div>
      </div>

      {/* Stat Cards (Matching Image 4) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Assigned Classes"
          value="3 Sections"
          icon={<BookOpen size={20} />}
          trend="Fall 2026 Active"
          trendUp={true}
          badge="Active"
        />
        <StatCard
          title="Total Students"
          value="125"
          icon={<Users size={20} />}
          avatars={[
            'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&auto=format&fit=crop&q=80',
          ]}
          moreAvatarsCount={122}
        />
        <StatCard
          title="Today Present"
          value="108 / 125"
          icon={<UserCheck size={20} />}
          trend="86.4% Attendance"
          trendUp={true}
        />
        <StatCard
          title="Average Rate"
          value="87%"
          icon={<Percent size={20} />}
          trend="+3.2% vs Dept Average"
          trendUp={true}
          badge="Top Rated"
        />
      </div>

      {/* Assigned Classes Grid (Matching Image 3 Team Cards) */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">Your Course Offerings & Sections</h3>
            <p className="text-xs text-slate-400 font-medium">Select a section to inspect roster and logs</p>
          </div>
          <span className="text-xs font-bold text-brand-600 hover:text-brand-700 cursor-pointer">
            Manage Schedules →
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {assignedClasses.map((cls) => {
            const isSelected = selectedClass === cls.id;
            return (
              <div
                key={cls.id}
                onClick={() => setSelectedClass(cls.id)}
                className={`bg-white rounded-2xl p-5 border cursor-pointer transition-all duration-300 ${
                  isSelected
                    ? 'border-brand-600 ring-2 ring-brand-500/20 shadow-soft-lg'
                    : 'border-slate-100 hover:border-slate-200 shadow-soft'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-brand-50 text-brand-700">
                      {cls.courseCode}
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm mt-1.5">{cls.courseName}</h4>
                    <p className="text-xs font-semibold text-brand-600 mt-0.5">{cls.section}</p>
                  </div>
                  {/* Overlapping Avatars (Image 3 style) */}
                  <div className="flex items-center -space-x-2">
                    {cls.avatars.map((img, i) => (
                      <img
                        key={i}
                        src={img}
                        alt="student"
                        className="w-7 h-7 rounded-full object-cover ring-2 ring-white"
                      />
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-50 flex items-center justify-between text-xs text-slate-400">
                  <span>{cls.time}</span>
                  <span className="font-bold text-slate-700">{cls.room}</span>
                </div>

                <div className="mt-3">
                  <div className="flex justify-between items-center text-[11px] font-bold text-slate-500 mb-1.5">
                    <span>Attendance Rate</span>
                    <span className="text-slate-800">{cls.attendanceRate}%</span>
                  </div>
                  <SegmentedProgress percentage={cls.attendanceRate} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Analytics & Attendance Growth Chart (Matching Image 4) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-soft border border-slate-100">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-bold text-slate-900 tracking-tight">Weekly Attendance Trend</h3>
              <p className="text-xs text-slate-400">Daily presence recorded by Edge AI Webcam</p>
            </div>
            <span className="text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1 rounded-xl">
              11 - 17 Mar 2026 ▾
            </span>
          </div>

          {/* Bar Chart Visualization (Image 4 style) */}
          <div className="h-48 flex items-end justify-between gap-3 px-4 pt-8">
            {attendanceTrend.map((item, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                {item.active && (
                  <div className="absolute -top-7 bg-slate-900 text-white text-[10px] font-bold px-2 py-1 rounded-md shadow-md whitespace-nowrap">
                    {item.tooltip}
                  </div>
                )}
                <div className="w-full max-w-[38px] bg-slate-100 rounded-t-xl h-36 flex flex-col justify-end overflow-hidden">
                  <div
                    className={`w-full rounded-t-xl transition-all duration-500 ${
                      item.active ? 'bg-brand-600 shadow-sm shadow-brand-500/50' : 'bg-brand-400/80 group-hover:bg-brand-500'
                    }`}
                    style={{ height: `${item.height}%` }}
                  ></div>
                </div>
                <span className="text-[11px] font-bold text-slate-400">{item.day}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Edge Node Camera Status Card (Image 4 "List Techs" style) */}
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-slate-100 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900 tracking-tight">Edge AI Camera Status</h3>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700">Active Node</span>
                <span className="text-xs font-mono font-bold text-brand-600 bg-brand-50 px-2 py-0.5 rounded">
                  LAPTOP-01
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">Camera Source</span>
                <span className="text-xs font-medium text-slate-700">WEBCAM-01 (Lab 1)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">Recognition Model</span>
                <span className="text-xs font-medium text-slate-700">ArcFace + SCRFD</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">Anti-Spoofing</span>
                <span className="text-xs font-bold text-emerald-600">MiniFASNet (Active)</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => window.location.assign('/dashboard/monitoring')}
            className="w-full mt-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all text-center"
          >
            Launch Live Feed Console
          </button>
        </div>
      </div>

      {/* Class Students Roster Table (Matching Image 2) */}
      <DataTable
        title={`Student Roster • ${assignedClasses.find((c) => c.id === selectedClass)?.courseName || 'Class'}`}
        subtitle="Individual presence, enrollment standing, and AI verification logs"
        data={studentsList}
        columns={columns}
        searchPlaceholder="Search student by name or roll number..."
        onExport={() => alert('Exporting Class Roster CSV...')}
      />
    </div>
  );
};
