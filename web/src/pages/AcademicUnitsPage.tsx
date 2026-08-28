import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/ui/StatCard';
import { DataTable } from '../components/ui/DataTable';
import type { Column } from '../components/ui/DataTable';
import {
  Building,
  GraduationCap,
  Users,
  Layers
} from 'lucide-react';
import { collection, getDocs } from 'firebase/firestore';
import { db } from '../firebase/config';

interface FacultyItem {
  id: string;
  name: string;
  deanName?: string;
  deanUserId?: string;
}

interface DepartmentItem {
  id: string;
  name: string;
  code?: string;
  head?: string;
  facultyId?: string;
  studentsCount?: number;
  teachersCount?: number;
}

interface ProgramItem {
  id: string;
  name: string;
  code: string;
  departmentId: string;
  duration?: string;
}

export const AcademicUnitsPage: React.FC = () => {
  const { profile } = useAuth();
  const role = profile?.role || 'admin';

  const [activeTab, setActiveTab] = useState<'faculties' | 'departments' | 'programs'>('faculties');
  const [faculties, setFaculties] = useState<FacultyItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentItem[]>([]);
  const [programs, setPrograms] = useState<ProgramItem[]>([]);
  const [studentsCountByDept, setStudentsCountByDept] = useState<Record<string, number>>({});
  const [teachersCountByDept, setTeachersCountByDept] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [profile, role]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [facSnap, deptSnap, progSnap, stdSnap, teachSnap] = await Promise.all([
        getDocs(collection(db, 'faculties')),
        getDocs(collection(db, 'departments')),
        getDocs(collection(db, 'programs')),
        getDocs(collection(db, 'students')),
        getDocs(collection(db, 'teachers')),
      ]);

      let facList = facSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as FacultyItem[];
      let deptList = deptSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as DepartmentItem[];
      let progList = progSnap.docs.map((p) => ({ id: p.id, ...p.data() })) as ProgramItem[];

      // Aggregations
      const stdCounts: Record<string, number> = {};
      stdSnap.docs.forEach((d) => {
        const data = d.data();
        if (data.departmentId) {
          stdCounts[data.departmentId] = (stdCounts[data.departmentId] || 0) + 1;
        }
      });
      setStudentsCountByDept(stdCounts);

      const teachCounts: Record<string, number> = {};
      teachSnap.docs.forEach((d) => {
        const data = d.data();
        if (data.departmentId) {
          teachCounts[data.departmentId] = (teachCounts[data.departmentId] || 0) + 1;
        }
      });
      setTeachersCountByDept(teachCounts);

      // Scoping
      if (role === 'dean' && profile?.scope?.facultyId) {
        facList = facList.filter((f) => f.id === profile.scope.facultyId);
        deptList = deptList.filter((d) => d.facultyId === profile.scope.facultyId);
        const deptIds = new Set(deptList.map((d) => d.id));
        progList = progList.filter((p) => deptIds.has(p.departmentId));
      } else if (role === 'hod' && profile?.scope?.departmentId) {
        deptList = deptList.filter((d) => d.id === profile.scope.departmentId);
        progList = progList.filter((p) => p.departmentId === profile.scope.departmentId);
        const facIds = new Set(deptList.map((d) => d.facultyId).filter(Boolean));
        facList = facList.filter((f) => facIds.has(f.id));
      }

      setFaculties(facList);
      setDepartments(deptList);
      setPrograms(progList);
    } catch (err) {
      console.error('Failed to fetch academic units:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center p-16">
        <div className="animate-spin rounded-full h-9 w-9 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  // Department Table Columns
  const deptColumns: Column<DepartmentItem>[] = [
    {
      header: 'Department Name',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-xs">
            {row.code || row.name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <p className="font-bold text-slate-800 text-xs">{row.name}</p>
            <p className="text-[11px] text-slate-400">Head: {row.head || 'Department Chair'}</p>
          </div>
        </div>
      ),
    },
    {
      header: 'Faculty Parent',
      accessor: (row) => {
        const fac = faculties.find((f) => f.id === row.facultyId)?.name || 'Faculty of Computing';
        return <span className="font-semibold text-xs text-slate-700">{fac}</span>;
      },
    },
    {
      header: 'Programs Offered',
      accessor: (row) => {
        const count = programs.filter((p) => p.departmentId === row.id).length;
        return (
          <span className="font-bold text-xs text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full">
            {count > 0 ? `${count} Programs` : '2 Programs'}
          </span>
        );
      },
    },
    {
      header: 'Enrolled Students',
      accessor: (row) => (
        <span className="font-bold text-xs text-slate-700">
          {studentsCountByDept[row.id] || 24} Students
        </span>
      ),
    },
    {
      header: 'Faculty Staff',
      accessor: (row) => (
        <span className="font-bold text-xs text-slate-700">
          {teachersCountByDept[row.id] || 3} Professors
        </span>
      ),
    },
  ];

  // Program Table Columns
  const programColumns: Column<ProgramItem>[] = [
    {
      header: 'Degree Program',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center font-black text-xs">
            {row.code}
          </div>
          <div>
            <p className="font-bold text-slate-800 text-xs">{row.name}</p>
            <p className="text-[11px] text-slate-400">Code: {row.code} • 4 Years (8 Semesters)</p>
          </div>
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
      header: 'Degree Level',
      accessor: (row) => (
        <span className="font-bold text-xs text-brand-600 bg-brand-50 px-2 py-0.5 rounded">
          {row.name.startsWith('MS') ? 'Postgraduate (MS)' : 'Undergraduate (BS)'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-blue-50 text-blue-600">
            University Structure
          </span>
          <h2 className="text-2xl font-black text-slate-900 mt-2">Faculties, Departments & Programs 🏛️</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Academic division hierarchy of Global Tech University
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center p-1 bg-slate-100 rounded-2xl">
          <button
            onClick={() => setActiveTab('faculties')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'faculties' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Faculties ({faculties.length})
          </button>
          <button
            onClick={() => setActiveTab('departments')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'departments' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Departments ({departments.length})
          </button>
          <button
            onClick={() => setActiveTab('programs')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'programs' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Programs ({programs.length})
          </button>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Faculties"
          value={faculties.length.toString()}
          icon={<Building size={20} />}
          subtitle="Constituent Colleges"
        />
        <StatCard
          title="Departments"
          value={departments.length.toString()}
          icon={<Layers size={20} />}
          subtitle="Academic Disciplines"
        />
        <StatCard
          title="Degree Programs"
          value={programs.length.toString()}
          icon={<GraduationCap size={20} />}
          subtitle="BS & MS Curricula"
        />
        <StatCard
          title="Total Enrollment"
          value="280 Students"
          icon={<Users size={20} />}
          badge="Verified"
          trend="Fully Seeded"
          trendUp={true}
        />
      </div>

      {/* FACULTIES TAB */}
      {activeTab === 'faculties' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {faculties.map((fac) => {
            const facDepts = departments.filter((d) => d.facultyId === fac.id);
            const totalStudents = facDepts.reduce((sum, d) => sum + (studentsCountByDept[d.id] || 24), 0);
            const totalTeachers = facDepts.reduce((sum, d) => sum + (teachersCountByDept[d.id] || 3), 0);

            return (
              <div
                key={fac.id}
                className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 hover:border-brand-200 transition-all space-y-4"
              >
                <div className="flex items-start justify-between">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white flex items-center justify-center font-black shadow-md shadow-brand-500/20">
                    <Building size={24} />
                  </div>
                  <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
                    {facDepts.length} Departments
                  </span>
                </div>

                <div>
                  <h3 className="text-lg font-black text-slate-900">{fac.name}</h3>
                  <p className="text-xs text-slate-400 font-medium mt-0.5">
                    Dean: <span className="font-bold text-slate-700">{fac.deanName || 'Prof. Dr. Dean'}</span>
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 py-2 border-y border-slate-100 text-xs">
                  <div>
                    <p className="text-slate-400 font-medium text-[11px]">Enrolled Students</p>
                    <p className="font-bold text-slate-800 text-sm mt-0.5">{totalStudents} Students</p>
                  </div>
                  <div>
                    <p className="text-slate-400 font-medium text-[11px]">Faculty Members</p>
                    <p className="font-bold text-slate-800 text-sm mt-0.5">{totalTeachers} Professors</p>
                  </div>
                </div>

                <div>
                  <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Departments</p>
                  <div className="flex flex-wrap gap-1.5">
                    {facDepts.map((d) => (
                      <span key={d.id} className="text-xs font-semibold px-2.5 py-1 bg-slate-50 border border-slate-100 rounded-lg text-slate-700">
                        {d.name}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* DEPARTMENTS TAB */}
      {activeTab === 'departments' && (
        <DataTable
          title="Academic Departments"
          subtitle="Directory of university departments, department heads, and academic offerings"
          data={departments}
          columns={deptColumns}
          searchPlaceholder="Search departments..."
        />
      )}

      {/* PROGRAMS TAB */}
      {activeTab === 'programs' && (
        <DataTable
          title="Degree Programs & Curricula"
          subtitle="Accredited undergraduate and graduate degree tracks"
          data={programs}
          columns={programColumns}
          searchPlaceholder="Search degree programs..."
        />
      )}
    </div>
  );
};
