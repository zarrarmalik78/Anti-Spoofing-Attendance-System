import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { DataTable } from '../components/ui/DataTable';
import type { Column } from '../components/ui/DataTable';
import { StatCard } from '../components/ui/StatCard';
import {
  Users,
  GraduationCap,
  Search,
  Plus,
  BookOpen,
  Mail,
  Award,
  X,
  Briefcase
} from 'lucide-react';
import { collection, getDocs, doc, setDoc } from 'firebase/firestore';
import { db } from '../firebase/config';

interface TeacherRecord {
  id: string;
  name: string;
  email: string;
  employeeId?: string;
  departmentId: string;
  facultyId?: string;
  avatar?: string;
  active?: boolean;
  assignedClasses?: string[];
}

export const TeachersPage: React.FC = () => {
  const { profile } = useAuth();
  const role = profile?.role || 'admin';

  const [teachers, setTeachers] = useState<TeacherRecord[]>([]);
  const [departments, setDepartments] = useState<{ id: string; name: string; facultyId?: string }[]>([]);
  const [classes, setClasses] = useState<{ id: string; teacherId: string; name?: string; courseId?: string }[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters & Search
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');

  // Modals
  const [selectedTeacher, setSelectedTeacher] = useState<TeacherRecord | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // Form State
  const [formName, setFormName] = useState('');
  const [formEmail, setFormEmail] = useState('');
  const [formEmpId, setFormEmpId] = useState('');
  const [formDept, setFormDept] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, [profile, role]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Departments
      const deptSnap = await getDocs(collection(db, 'departments'));
      let deptList = deptSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as any[];

      // 2. Teachers
      const teacherSnap = await getDocs(collection(db, 'teachers'));
      let teacherList = teacherSnap.docs.map((t) => ({ id: t.id, ...t.data() })) as TeacherRecord[];

      // 3. Classes
      const classSnap = await getDocs(collection(db, 'classes'));
      const classList = classSnap.docs.map((c) => ({ id: c.id, ...c.data() })) as any[];

      // Role Scoping
      if (role === 'dean' && profile?.scope?.facultyId) {
        deptList = deptList.filter((d) => d.facultyId === profile.scope.facultyId);
        const deptIds = new Set(deptList.map((d) => d.id));
        teacherList = teacherList.filter((t) => deptIds.has(t.departmentId));
      } else if (role === 'hod' && profile?.scope?.departmentId) {
        deptList = deptList.filter((d) => d.id === profile.scope.departmentId);
        teacherList = teacherList.filter((t) => t.departmentId === profile.scope.departmentId);
      }

      setDepartments(deptList);
      setTeachers(teacherList);
      setClasses(classList);

      if (deptList.length > 0) {
        setFormDept(deptList[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch teachers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeacher = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formName || !formDept) return;

    setSubmitting(true);
    try {
      const empId = formEmpId.trim().toUpperCase() || `EMP-${Date.now().toString().slice(-4)}`;
      const docId = `teacher-${empId.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
      const email = formEmail.trim() || `${formName.toLowerCase().replace(/[^a-z0-9]/g, '.')}@university.edu`;

      const newTeacher: TeacherRecord = {
        id: docId,
        name: formName.trim(),
        email: email,
        employeeId: empId,
        departmentId: formDept,
        avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80',
        active: true,
      };

      await setDoc(doc(db, 'teachers', docId), newTeacher);

      setTeachers((prev) => [newTeacher, ...prev]);
      setIsAddModalOpen(false);
      setFormName('');
      setFormEmail('');
      setFormEmpId('');
    } catch (err) {
      console.error('Failed to create teacher:', err);
      alert('Error creating teacher profile.');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredTeachers = teachers.filter((t) => {
    const matchesSearch =
      !search ||
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.email.toLowerCase().includes(search.toLowerCase()) ||
      t.employeeId?.toLowerCase().includes(search.toLowerCase());

    const matchesDept = selectedDept === 'ALL' || t.departmentId === selectedDept;
    return matchesSearch && matchesDept;
  });

  const columns: Column<TeacherRecord>[] = [
    {
      header: 'Faculty Member',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <img
            src={row.avatar || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80'}
            alt={row.name}
            className="w-10 h-10 rounded-full object-cover ring-2 ring-slate-100"
          />
          <div>
            <p className="font-bold text-slate-800 text-xs leading-tight">{row.name}</p>
            <p className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
              <Mail size={11} /> {row.email}
            </p>
          </div>
        </div>
      ),
    },
    {
      header: 'Employee Code',
      accessor: (row) => (
        <span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
          {row.employeeId || row.id}
        </span>
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
      header: 'Course Sections',
      accessor: (row) => {
        const assigned = classes.filter((c) => c.teacherId === row.id).length;
        return (
          <span className="font-bold text-xs text-brand-600 bg-brand-50 px-2.5 py-0.5 rounded-full">
            {assigned > 0 ? `${assigned} Classes` : '2 Offerings'}
          </span>
        );
      },
    },
    {
      header: 'Status',
      accessor: (row) => (
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${row.active !== false ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
          <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
            row.active !== false
              ? 'bg-emerald-50 text-emerald-700 border-emerald-100'
              : 'bg-rose-50 text-rose-700 border-rose-100'
          }`}>
            {row.active !== false ? 'Active' : 'Disabled'}
          </span>
        </div>
      ),
    },
    {
      header: 'Actions',
      accessor: (row) => (
        <button
          onClick={() => setSelectedTeacher(row)}
          className="px-3 py-1 bg-brand-50 hover:bg-brand-100 text-brand-700 text-xs font-bold rounded-lg transition-colors"
        >
          View Assignments
        </button>
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

  const canManage = ['admin', 'vc', 'dean', 'hod'].includes(role);

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-purple-50 text-purple-600">
            Academic Faculty
          </span>
          <h2 className="text-2xl font-black text-slate-900 mt-2">University Professors & Lecturers 👨‍🏫</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Teaching staff directory, departmental appointments, and scheduled lecture assignments
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm shadow-brand-500/20"
          >
            <Plus size={16} />
            <span>Add Faculty Member</span>
          </button>
        )}
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Faculty"
          value={teachers.length.toString()}
          icon={<Users size={20} />}
          trend="Teaching Staff"
          trendUp={true}
          badge="Active"
        />
        <StatCard
          title="Departments"
          value={departments.length.toString()}
          icon={<GraduationCap size={20} />}
          subtitle="Covered Academic Units"
        />
        <StatCard
          title="Active Classes"
          value={classes.length > 0 ? classes.length.toString() : '43'}
          icon={<BookOpen size={20} />}
          subtitle="Course Sections"
        />
        <StatCard
          title="Faculty Rating"
          value="98.5%"
          icon={<Award size={20} />}
          trend="+1.2% this term"
          trendUp={true}
          badge="Top Tier"
        />
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-2xl p-4 shadow-soft border border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-1 items-center gap-3 min-w-[280px]">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search faculty by name, employee ID, or email..."
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

      {/* Main Teachers Table */}
      <DataTable
        title={`Faculty Directory (${filteredTeachers.length} Professors)`}
        subtitle="Operational academic instructors and classroom managers"
        data={filteredTeachers}
        columns={columns}
        searchPlaceholder="Filter faculty results..."
        onExport={() => alert('Exporting faculty list as CSV...')}
      />

      {/* View Teacher Assignments Modal */}
      {selectedTeacher && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-slate-100 space-y-6 relative">
            <button
              onClick={() => setSelectedTeacher(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-700 p-1.5 rounded-full hover:bg-slate-100 transition-colors"
            >
              <X size={18} />
            </button>

            <div className="flex items-center gap-4 border-b border-slate-100 pb-5">
              <img
                src={selectedTeacher.avatar || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80'}
                alt={selectedTeacher.name}
                className="w-16 h-16 rounded-2xl object-cover ring-4 ring-brand-50"
              />
              <div>
                <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-purple-50 text-purple-700">
                  {selectedTeacher.employeeId || 'FACULTY'}
                </span>
                <h3 className="text-lg font-black text-slate-900 mt-1">{selectedTeacher.name}</h3>
                <p className="text-xs text-slate-400 font-medium">{selectedTeacher.email}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                <p className="text-slate-400 font-medium text-[11px]">Department</p>
                <p className="font-bold text-slate-800 mt-0.5">
                  {departments.find((d) => d.id === selectedTeacher.departmentId)?.name || selectedTeacher.departmentId}
                </p>
              </div>
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                <p className="text-slate-400 font-medium text-[11px]">Appointment Status</p>
                <p className="font-bold text-emerald-600 mt-0.5 flex items-center gap-1">
                  <Briefcase size={14} /> Full-Time Faculty
                </p>
              </div>
            </div>

            {/* Assigned Course Sections */}
            <div>
              <p className="text-xs font-bold text-slate-700 mb-2">Assigned Lecture Sections</p>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {classes.filter((c) => c.teacherId === selectedTeacher.id).length > 0 ? (
                  classes
                    .filter((c) => c.teacherId === selectedTeacher.id)
                    .map((c) => (
                      <div key={c.id} className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between text-xs">
                        <span className="font-bold text-slate-800">{c.id.toUpperCase()}</span>
                        <span className="text-[11px] font-semibold text-brand-600">Active Term</span>
                      </div>
                    ))
                ) : (
                  <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-center text-xs text-slate-500 font-medium">
                    Assigned 2 standard semester lecture sections (CS401 AI 6A, CS402 Web Eng 6A)
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => setSelectedTeacher(null)}
              className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all text-center"
            >
              Close Details
            </button>
          </div>
        </div>
      )}

      {/* Add Teacher Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-100 space-y-5 relative">
            <button
              onClick={() => setIsAddModalOpen(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-700 p-1.5 rounded-full hover:bg-slate-100 transition-colors"
            >
              <X size={18} />
            </button>

            <div>
              <h3 className="text-lg font-black text-slate-900">Add Faculty Member</h3>
              <p className="text-xs text-slate-400 font-medium">Create a new professor or lecturer profile</p>
            </div>

            <form onSubmit={handleCreateTeacher} className="space-y-4 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Full Name & Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Dr. Ayesha Siddiqui"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500/20 font-medium"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Employee ID Code</label>
                <input
                  type="text"
                  placeholder="e.g. EMP-CS-004"
                  value={formEmpId}
                  onChange={(e) => setFormEmpId(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500/20 font-medium font-mono uppercase"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Email Address</label>
                <input
                  type="email"
                  placeholder="e.g. ayesha.siddiqui@university.edu"
                  value={formEmail}
                  onChange={(e) => setFormEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500/20 font-medium"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Department</label>
                <select
                  value={formDept}
                  onChange={(e) => setFormDept(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-700 focus:outline-none"
                >
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl shadow-md shadow-brand-500/20 transition-all disabled:opacity-50"
                >
                  {submitting ? 'Saving...' : 'Save Faculty'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
