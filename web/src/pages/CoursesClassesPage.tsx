import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/ui/StatCard';
import { DataTable } from '../components/ui/DataTable';
import type { Column } from '../components/ui/DataTable';
import {
  BookOpen,
  Calendar,
  Clock,
  MapPin,
  Users,
  Search
} from 'lucide-react';
import { collection, getDocs } from 'firebase/firestore';
import { db } from '../firebase/config';

interface CourseItem {
  id: string;
  code: string;
  name: string;
  creditHours: number;
  departmentId: string;
}

interface ClassItem {
  id: string;
  courseId: string;
  teacherId: string;
  programId: string;
  departmentId: string;
  semester: string;
  section: string;
  academicYear: string;
  schedule: string;
  room: string;
  active: boolean;
}

export const CoursesClassesPage: React.FC = () => {
  const { profile } = useAuth();
  const role = profile?.role || 'admin';

  const [activeTab, setActiveTab] = useState<'classes' | 'courses'>('classes');
  const [courses, setCourses] = useState<CourseItem[]>([]);
  const [classes, setClasses] = useState<ClassItem[]>([]);
  const [departments, setDepartments] = useState<{ id: string; name: string }[]>([]);
  const [teachers, setTeachers] = useState<{ id: string; name: string }[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters & Search
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');

  useEffect(() => {
    fetchData();
  }, [profile, role]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [crsSnap, clsSnap, deptSnap, tchSnap] = await Promise.all([
        getDocs(collection(db, 'courses')),
        getDocs(collection(db, 'classes')),
        getDocs(collection(db, 'departments')),
        getDocs(collection(db, 'teachers')),
      ]);

      let crsList = crsSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as CourseItem[];
      let clsList = clsSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as ClassItem[];
      let deptList = deptSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as any[];
      let tchList = tchSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as any[];

      // Scope Filtering
      if (role === 'dean' && profile?.scope?.facultyId) {
        deptList = deptList.filter((d) => d.facultyId === profile.scope.facultyId);
        const deptIds = new Set(deptList.map((d) => d.id));
        crsList = crsList.filter((c) => deptIds.has(c.departmentId));
        clsList = clsList.filter((c) => deptIds.has(c.departmentId));
      } else if (role === 'hod' && profile?.scope?.departmentId) {
        deptList = deptList.filter((d) => d.id === profile.scope.departmentId);
        crsList = crsList.filter((c) => c.departmentId === profile.scope.departmentId);
        clsList = clsList.filter((c) => c.departmentId === profile.scope.departmentId);
      } else if (role === 'teacher' && profile?.scope?.teacherId) {
        clsList = clsList.filter((c) => c.teacherId === profile.scope.teacherId);
      } else if (role === 'student' && profile?.scope?.studentId) {
        // Enrolled classes for student
        const stdSnap = await getDocs(collection(db, 'students'));
        const currentStudent = stdSnap.docs
          .map((d) => d.data())
          .find((s: any) => s.studentId === profile.scope?.studentId || s.rollNumber === profile.scope?.studentId);
        if (currentStudent && currentStudent.classIds) {
          const enrolledSet = new Set(currentStudent.classIds);
          clsList = clsList.filter((c) => enrolledSet.has(c.id));
        }
      }

      setCourses(crsList);
      setClasses(clsList);
      setDepartments(deptList);
      setTeachers(tchList);
    } catch (err) {
      console.error('Failed to fetch courses & classes:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredClasses = classes.filter((c) => {
    const crsName = courses.find((crs) => crs.id === c.courseId)?.name || '';
    const matchesSearch =
      !search ||
      c.id.toLowerCase().includes(search.toLowerCase()) ||
      crsName.toLowerCase().includes(search.toLowerCase()) ||
      c.room.toLowerCase().includes(search.toLowerCase());

    const matchesDept = selectedDept === 'ALL' || c.departmentId === selectedDept;
    return matchesSearch && matchesDept;
  });

  const filteredCourses = courses.filter((crs) => {
    const matchesSearch =
      !search ||
      crs.name.toLowerCase().includes(search.toLowerCase()) ||
      crs.code.toLowerCase().includes(search.toLowerCase());

    const matchesDept = selectedDept === 'ALL' || crs.departmentId === selectedDept;
    return matchesSearch && matchesDept;
  });

  // Class Offerings Columns
  const classColumns: Column<ClassItem>[] = [
    {
      header: 'Course & Section',
      accessor: (row) => {
        const crs = courses.find((c) => c.id === row.courseId);
        return (
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-black text-xs">
              {crs?.code || 'CS'}
            </div>
            <div>
              <p className="font-bold text-slate-800 text-xs leading-tight">
                {crs?.name || 'Academic Course'}
              </p>
              <p className="text-[11px] text-slate-400 font-medium mt-0.5">
                Semester {row.semester}{row.section} • {row.academicYear || 'Fall 2026'}
              </p>
            </div>
          </div>
        );
      },
    },
    {
      header: 'Instructor',
      accessor: (row) => {
        const teacher = teachers.find((t) => t.id === row.teacherId);
        return (
          <div>
            <p className="font-bold text-xs text-slate-700">{teacher?.name || 'Faculty Lecturer'}</p>
            <p className="text-[10px] text-slate-400 font-medium">Assigned Instructor</p>
          </div>
        );
      },
    },
    {
      header: 'Schedule & Timetable',
      accessor: (row) => (
        <div className="flex items-center gap-1.5 text-xs text-slate-700 font-medium">
          <Clock size={13} className="text-brand-600 shrink-0" />
          <span>{row.schedule || 'Mon/Wed 08:30 AM - 10:00 AM'}</span>
        </div>
      ),
    },
    {
      header: 'Room',
      accessor: (row) => (
        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg w-max">
          <MapPin size={12} className="text-slate-400" />
          <span>{row.room || 'Room 301'}</span>
        </div>
      ),
    },
    {
      header: 'Enrolled Cohort',
      accessor: () => (
        <span className="font-bold text-xs text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full">
          24 Students
        </span>
      ),
    },
  ];

  // Course Catalog Columns
  const courseColumns: Column<CourseItem>[] = [
    {
      header: 'Course Code & Title',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs font-bold text-brand-600 bg-brand-50 px-2 py-0.5 rounded">
            {row.code}
          </span>
          <p className="font-bold text-slate-800 text-xs">{row.name}</p>
        </div>
      ),
    },
    {
      header: 'Department',
      accessor: (row) => {
        const dept = departments.find((d) => d.id === row.departmentId)?.name || row.departmentId;
        return <span className="font-semibold text-xs text-slate-700">{dept}</span>;
      },
    },
    {
      header: 'Credit Hours',
      accessor: (row) => (
        <span className="font-bold text-xs text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">
          {row.creditHours || 3} Credits (3-0)
        </span>
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
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-600">
            Curriculum & Classes
          </span>
          <h2 className="text-2xl font-black text-slate-900 mt-2">Courses & Active Class Offerings 📖</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Timetables, lecture room assignments, course syllabi, and section enrollment
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center p-1 bg-slate-100 rounded-2xl">
          <button
            onClick={() => setActiveTab('classes')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'classes' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Class Offerings ({classes.length})
          </button>
          <button
            onClick={() => setActiveTab('courses')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'courses' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Course Catalog ({courses.length})
          </button>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Active Classes"
          value={classes.length.toString()}
          icon={<Calendar size={20} />}
          trend="Current Term"
          trendUp={true}
          badge="In Session"
        />
        <StatCard
          title="Course Catalog"
          value={courses.length.toString()}
          icon={<BookOpen size={20} />}
          subtitle="Accredited Modules"
        />
        <StatCard
          title="Classrooms Assigned"
          value="18 Rooms"
          icon={<MapPin size={20} />}
          subtitle="Smart IoT Lecture Halls"
        />
        <StatCard
          title="Average Capacity"
          value="24 Students"
          icon={<Users size={20} />}
          subtitle="Per Section"
        />
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-2xl p-4 shadow-soft border border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-1 items-center gap-3 min-w-[280px]">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder={`Search ${activeTab === 'classes' ? 'classes by title, code, room...' : 'courses by title, code...'}`}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
            <Search size={14} className="absolute left-3 top-2.5 text-slate-400 pointer-events-none" />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="px-3.5 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs font-bold text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tables */}
      {activeTab === 'classes' ? (
        <DataTable
          title={`Scheduled Class Offerings (${filteredClasses.length})`}
          subtitle="Active semester timetable with assigned lecture halls and instructors"
          data={filteredClasses}
          columns={classColumns}
          searchPlaceholder="Filter classes..."
        />
      ) : (
        <DataTable
          title={`Academic Course Catalog (${filteredCourses.length} Courses)`}
          subtitle="Undergraduate and postgraduate accredited syllabus"
          data={filteredCourses}
          columns={courseColumns}
          searchPlaceholder="Filter course modules..."
        />
      )}
    </div>
  );
};
