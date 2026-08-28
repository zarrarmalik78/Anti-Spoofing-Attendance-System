import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { DataTable } from '../components/ui/DataTable';
import type { Column } from '../components/ui/DataTable';
import { StatCard } from '../components/ui/StatCard';
import {
  Users,
  Shield,
  Search,
  Plus,
  Mail,
  UserCheck,
  UserX,
  X,
  Lock
} from 'lucide-react';
import { collection, getDocs, doc, setDoc, updateDoc } from 'firebase/firestore';
import { db } from '../firebase/config';

interface UserRecord {
  id: string;
  uid?: string;
  name: string;
  email: string;
  role: string;
  active: boolean;
  hasAuthAccount: boolean;
  studentId?: string;
  employeeId?: string;
  rollNumber?: string;
  scope?: {
    level?: string;
    universityId?: string;
    facultyId?: string;
    departmentId?: string;
    teacherId?: string;
    studentId?: string;
  };
  departmentId?: string;
  facultyId?: string;
}

export const UsersPage: React.FC = () => {
  const { profile } = useAuth();
  const currentRole = profile?.role || 'admin';

  const [users, setUsers] = useState<UserRecord[]>([]);
  const [departments, setDepartments] = useState<{ id: string; name: string; facultyId?: string }[]>([]);
  const [faculties, setFaculties] = useState<{ id: string; name: string }[]>([]);
  const [programs, setPrograms] = useState<{ id: string; name: string; departmentId: string }[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters & Search
  const [search, setSearch] = useState('');
  const [selectedRoleFilter, setSelectedRoleFilter] = useState('ALL');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState('ALL');

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // Add User Form State
  const [formName, setFormName] = useState('');
  const [formEmail, setFormEmail] = useState('');
  const [formPassword, setFormPassword] = useState('password123');
  const [formRole, setFormRole] = useState('student');
  const [formDept, setFormDept] = useState('');
  const [formFaculty, setFormFaculty] = useState('');
  const [formProgram, setFormProgram] = useState('');
  const [formSemester, setFormSemester] = useState('6');
  const [formSection, setFormSection] = useState('A');
  const [formRollNo, setFormRollNo] = useState('');
  const [formEmpId, setFormEmpId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Determine allowed roles that current user can create based on hierarchy
  const getAllowedRolesToCreate = (): string[] => {
    switch (currentRole) {
      case 'admin':
        return ['admin', 'vc', 'dean', 'hod', 'teacher', 'student'];
      case 'vc':
        return ['dean', 'hod', 'teacher', 'student'];
      case 'dean':
        return ['hod', 'teacher', 'student'];
      case 'hod':
        return ['teacher', 'student'];
      default:
        return [];
    }
  };

  const allowedRoles = getAllowedRolesToCreate();

  useEffect(() => {
    fetchData();
  }, [profile, currentRole]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Fetch Faculties, Depts, Programs, Users, Students, Teachers
      const [facSnap, deptSnap, progSnap, userSnap, studentSnap, teacherSnap] = await Promise.all([
        getDocs(collection(db, 'faculties')),
        getDocs(collection(db, 'departments')),
        getDocs(collection(db, 'programs')),
        getDocs(collection(db, 'users')),
        getDocs(collection(db, 'students')),
        getDocs(collection(db, 'teachers')),
      ]);

      let facList = facSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as any[];
      let deptList = deptSnap.docs.map((d) => ({ id: d.id, ...d.data() })) as any[];
      let progList = progSnap.docs.map((p) => ({ id: p.id, ...p.data() })) as any[];
      let userList = userSnap.docs.map((u) => ({ id: u.id, ...u.data() })) as any[];
      let studentList = studentSnap.docs.map((s) => ({ id: s.id, ...s.data() })) as any[];
      let teacherList = teacherSnap.docs.map((t) => ({ id: t.id, ...t.data() })) as any[];

      // Create lookup maps for linked Web Auth accounts
      const authMapByEmail = new Map<string, any>();
      const authMapByStudentId = new Map<string, any>();
      const authMapByTeacherId = new Map<string, any>();

      userList.forEach((u) => {
        if (u.email) authMapByEmail.set(u.email.toLowerCase(), u);
        if (u.scope?.studentId) authMapByStudentId.set(u.scope.studentId, u);
        if (u.scope?.teacherId) authMapByTeacherId.set(u.scope.teacherId, u);
        if (u.studentId) authMapByStudentId.set(u.studentId, u);
        if (u.teacherId) authMapByTeacherId.set(u.teacherId, u);
      });

      const unifiedRecords: UserRecord[] = [];
      const processedEmails = new Set<string>();

      // 1. Non-student/teacher leadership users (admin, vc, dean, hod)
      userList.forEach((u) => {
        if (['admin', 'vc', 'dean', 'hod'].includes(u.role)) {
          unifiedRecords.push({
            id: u.id,
            uid: u.uid || u.id,
            name: u.name || 'User',
            email: u.email || '',
            role: u.role,
            active: u.active !== false,
            hasAuthAccount: true,
            scope: u.scope || {},
            departmentId: u.scope?.departmentId || u.departmentId,
            facultyId: u.scope?.facultyId || u.facultyId,
          });
          if (u.email) processedEmails.add(u.email.toLowerCase());
        }
      });

      // 2. Teachers from 'teachers' collection
      teacherList.forEach((t) => {
        const linkedUser = authMapByEmail.get(t.email?.toLowerCase()) || authMapByTeacherId.get(t.id);
        const emailKey = t.email?.toLowerCase() || `teacher-${t.id}`;
        processedEmails.add(emailKey);

        unifiedRecords.push({
          id: linkedUser ? linkedUser.id : `teacher-rec-${t.id}`,
          uid: linkedUser ? linkedUser.id : undefined,
          name: t.name,
          email: t.email || `${t.id}@university.edu`,
          role: 'teacher',
          active: t.active !== false,
          hasAuthAccount: !!linkedUser,
          employeeId: t.employeeId || t.id,
          departmentId: t.departmentId,
          scope: linkedUser?.scope || { departmentId: t.departmentId, teacherId: t.id },
        });
      });

      // 3. Students from 'students' collection (260+ seeded university records!)
      studentList.forEach((s) => {
        const sId = s.studentId || s.rollNumber || s.id;
        const linkedUser = authMapByEmail.get(s.email?.toLowerCase()) || authMapByStudentId.get(sId);
        const emailKey = s.email?.toLowerCase() || `std-${sId}`;
        processedEmails.add(emailKey);

        unifiedRecords.push({
          id: linkedUser ? linkedUser.id : `student-rec-${s.id}`,
          uid: linkedUser ? linkedUser.id : undefined,
          name: s.name,
          email: s.email || `${sId.toLowerCase()}@university.edu`,
          role: 'student',
          active: s.active !== false,
          hasAuthAccount: !!linkedUser,
          studentId: sId,
          rollNumber: s.rollNumber || sId,
          departmentId: s.departmentId,
          scope: linkedUser?.scope || { studentId: sId, departmentId: s.departmentId },
        });
      });

      // Scope filtering based on role hierarchy
      let filteredList = unifiedRecords;
      if (currentRole === 'dean' && profile?.scope?.facultyId) {
        deptList = deptList.filter((d) => d.facultyId === profile.scope.facultyId);
        const deptIds = new Set(deptList.map((d) => d.id));
        progList = progList.filter((p) => deptIds.has(p.departmentId));

        filteredList = filteredList.filter((u) => {
          if (u.role === 'dean' && u.scope?.facultyId === profile.scope.facultyId) return true;
          if (u.scope?.facultyId === profile.scope.facultyId) return true;
          if (u.departmentId && deptIds.has(u.departmentId)) return true;
          if (u.scope?.departmentId && deptIds.has(u.scope.departmentId)) return true;
          return false;
        });
      } else if (currentRole === 'hod' && profile?.scope?.departmentId) {
        deptList = deptList.filter((d) => d.id === profile.scope.departmentId);
        progList = progList.filter((p) => p.departmentId === profile.scope.departmentId);
        filteredList = filteredList.filter(
          (u) =>
            u.departmentId === profile.scope.departmentId ||
            u.scope?.departmentId === profile.scope.departmentId ||
            (u.role === 'hod' && u.id === profile.uid)
        );
      } else if (currentRole === 'student' && profile?.scope?.studentId) {
        filteredList = filteredList.filter((u) => u.studentId === profile.scope?.studentId || u.email === profile.email);
      }

      setFaculties(facList);
      setDepartments(deptList);
      setPrograms(progList);
      setUsers(filteredList);

      if (deptList.length > 0) setFormDept(deptList[0].id);
      if (facList.length > 0) setFormFaculty(facList[0].id);
      if (progList.length > 0) setFormProgram(progList[0].id);
      if (allowedRoles.length > 0) setFormRole(allowedRoles[allowedRoles.length - 1]);
    } catch (err) {
      console.error('Failed to fetch user management data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (user: UserRecord) => {
    try {
      const newStatus = !user.active;
      if (user.hasAuthAccount && user.id) {
        await updateDoc(doc(db, 'users', user.id), { active: newStatus });
      }
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, active: newStatus } : u))
      );
    } catch (err) {
      console.error('Failed to update user status:', err);
      alert('Error updating user status.');
    }
  };

  const handleProvisionWebAccount = async (user: UserRecord) => {
    try {
      const userDocId = `user-${user.role}-${Date.now().toString().slice(-6)}`;
      const newUserDoc = {
        id: userDocId,
        uid: userDocId,
        name: user.name,
        email: user.email,
        role: user.role,
        active: true,
        scope: user.scope || {
          studentId: user.studentId,
          departmentId: user.departmentId,
        },
      };

      await setDoc(doc(db, 'users', userDocId), newUserDoc);

      setUsers((prev) =>
        prev.map((u) =>
          u.id === user.id
            ? { ...u, id: userDocId, uid: userDocId, hasAuthAccount: true, active: true }
            : u
        )
      );

      alert(`Web Login Account provisioned for ${user.name}!\nEmail: ${user.email}\nDefault Password: password123`);
    } catch (err) {
      console.error('Failed to provision web account:', err);
      alert('Error provisioning web login account.');
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formName || !formEmail) return;

    setSubmitting(true);
    try {
      // Build Scope
      const scope: Record<string, any> = {};
      if (formRole === 'admin') {
        scope.level = 'system';
      } else if (formRole === 'vc') {
        scope.universityId = 'univ-tech-01';
      } else if (formRole === 'dean') {
        scope.facultyId = formFaculty;
      } else if (formRole === 'hod') {
        scope.departmentId = formDept;
      } else if (formRole === 'teacher') {
        scope.departmentId = formDept;
        scope.teacherId = `teacher-${(formEmpId || formName).toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
      } else if (formRole === 'student') {
        scope.studentId = formRollNo.trim().toUpperCase() || `STD-${Date.now().toString().slice(-4)}`;
        scope.departmentId = formDept;
        scope.programId = formProgram;
      }

      const docId = `user-${formRole}-${Date.now().toString().slice(-6)}`;
      const newUser: UserRecord = {
        id: docId,
        uid: docId,
        name: formName.trim(),
        email: formEmail.trim().toLowerCase(),
        role: formRole,
        active: true,
        hasAuthAccount: true,
        scope: scope,
        studentId: scope.studentId,
        departmentId: formDept,
      };

      // 1. Create document in 'users' collection
      await setDoc(doc(db, 'users', docId), newUser);

      // 2. If student, also create student record in 'students' collection
      if (formRole === 'student') {
        const studentDocId = `student-${scope.studentId.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
        await setDoc(doc(db, 'students', studentDocId), {
          id: studentDocId,
          studentId: scope.studentId,
          rollNumber: scope.studentId,
          name: formName.trim(),
          email: formEmail.trim().toLowerCase(),
          departmentId: formDept,
          programId: formProgram,
          semester: formSemester,
          section: formSection,
          batch: 'FA24',
          active: true,
          authUid: docId,
          classIds: [],
        });
      }

      // 3. If teacher, also create teacher record in 'teachers' collection
      if (formRole === 'teacher') {
        const teacherDocId = scope.teacherId;
        await setDoc(doc(db, 'teachers', teacherDocId), {
          id: teacherDocId,
          name: formName.trim(),
          email: formEmail.trim().toLowerCase(),
          employeeId: formEmpId || 'EMP-001',
          departmentId: formDept,
          active: true,
          authUid: docId,
        });
      }

      setUsers((prev) => [newUser, ...prev]);
      setIsAddModalOpen(false);
      setFormName('');
      setFormEmail('');
      setFormRollNo('');
      setFormEmpId('');
      alert(`User account created successfully! Credentials: ${newUser.email} / ${formPassword}`);
    } catch (err) {
      console.error('Failed to create user:', err);
      alert('Error creating user account.');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      !search ||
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      u.role.toLowerCase().includes(search.toLowerCase()) ||
      (u.studentId && u.studentId.toLowerCase().includes(search.toLowerCase()));

    const matchesRole = selectedRoleFilter === 'ALL' || u.role === selectedRoleFilter;
    const matchesStatus =
      selectedStatusFilter === 'ALL' ||
      (selectedStatusFilter === 'ACTIVE' && u.active) ||
      (selectedStatusFilter === 'LINKED' && u.hasAuthAccount) ||
      (selectedStatusFilter === 'RECORD_ONLY' && !u.hasAuthAccount) ||
      (selectedStatusFilter === 'DISABLED' && !u.active);

    return matchesSearch && matchesRole && matchesStatus;
  });

  const getRoleBadgeStyle = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'vc':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'dean':
        return 'bg-blue-50 text-blue-800 border-blue-200';
      case 'hod':
        return 'bg-indigo-50 text-indigo-800 border-indigo-200';
      case 'teacher':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const columns: Column<UserRecord>[] = [
    {
      header: 'User Identity',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-brand-50 text-brand-700 font-black text-xs flex items-center justify-center ring-2 ring-slate-100">
            {row.name?.charAt(0) || 'U'}
          </div>
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
      header: 'Assigned Role',
      accessor: (row) => (
        <span
          className={`inline-block font-extrabold text-[10px] uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${getRoleBadgeStyle(
            row.role
          )}`}
        >
          {row.role}
        </span>
      ),
    },
    {
      header: 'RBAC Scope',
      accessor: (row) => {
        if (row.role === 'admin') return <span className="font-bold text-xs text-purple-600">System Wide</span>;
        if (row.role === 'vc') return <span className="font-bold text-xs text-amber-600">Campus Wide</span>;
        if (row.role === 'dean') {
          const facName = faculties.find((f) => f.id === row.scope?.facultyId)?.name || row.scope?.facultyId || 'Faculty';
          return <span className="font-medium text-xs text-slate-700">{facName}</span>;
        }
        if (row.role === 'hod' || row.role === 'teacher') {
          const deptName = departments.find((d) => d.id === (row.departmentId || row.scope?.departmentId))?.name || row.departmentId || 'Department';
          return <span className="font-medium text-xs text-slate-700">{deptName}</span>;
        }
        return (
          <span className="font-mono text-xs font-bold text-brand-600">
            {row.studentId || row.scope?.studentId || 'Enrolled Student'}
          </span>
        );
      },
    },
    {
      header: 'Web Access Status',
      accessor: (row) => (
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${row.hasAuthAccount ? 'bg-emerald-500' : 'bg-slate-400'}`}></span>
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1 ${
              row.hasAuthAccount
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-slate-100 text-slate-600 border-slate-200'
            }`}
          >
            {row.hasAuthAccount ? <Lock size={10} /> : null}
            {row.hasAuthAccount ? 'Web Account Linked' : 'University Record Only'}
          </span>
        </div>
      ),
    },
    {
      header: 'Actions',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          {!row.hasAuthAccount ? (
            <button
              onClick={() => handleProvisionWebAccount(row)}
              className="px-2.5 py-1 text-xs font-bold rounded-lg bg-brand-50 hover:bg-brand-100 text-brand-700 transition-colors flex items-center gap-1"
            >
              <Plus size={13} />
              <span>Enable Web Access</span>
            </button>
          ) : (
            <button
              onClick={() => handleToggleActive(row)}
              className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-colors flex items-center gap-1 ${
                row.active !== false
                  ? 'bg-rose-50 hover:bg-rose-100 text-rose-700'
                  : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700'
              }`}
            >
              {row.active !== false ? <UserX size={13} /> : <UserCheck size={13} />}
              <span>{row.active !== false ? 'Deactivate' : 'Activate'}</span>
            </button>
          )}
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

  const canCreate = allowedRoles.length > 0;

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-brand-50 text-brand-600">
            RBAC & User Access
          </span>
          <h2 className="text-2xl font-black text-slate-900 mt-2">User Accounts & Roles 🛡️</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Manage university credentials, role assignments, department scopes, and active account access
          </p>
        </div>

        {canCreate && (
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm shadow-brand-500/20"
          >
            <Plus size={16} />
            <span>Create New User</span>
          </button>
        )}
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total User Accounts"
          value={users.length.toString()}
          icon={<Users size={20} />}
          trend="In Firestore"
          trendUp={true}
          badge="Synchronized"
        />
        <StatCard
          title="Active Accounts"
          value={users.filter((u) => u.active !== false).length.toString()}
          icon={<UserCheck size={20} />}
          subtitle="Allowed Authentication"
        />
        <StatCard
          title="Disabled Accounts"
          value={users.filter((u) => u.active === false).length.toString()}
          icon={<UserX size={20} />}
          subtitle="Access Restricted"
        />
        <StatCard
          title="Hierarchy Level"
          value={currentRole.toUpperCase()}
          icon={<Shield size={20} />}
          subtitle={`Can Manage: ${allowedRoles.join(', ') || 'None'}`}
        />
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-2xl p-4 shadow-soft border border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-1 items-center gap-3 min-w-[280px]">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search by name, email, or role..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
            <Search size={14} className="absolute left-3 top-2.5 text-slate-400 pointer-events-none" />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedRoleFilter}
            onChange={(e) => setSelectedRoleFilter(e.target.value)}
            className="px-3.5 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs font-bold text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Roles</option>
            {['admin', 'vc', 'dean', 'hod', 'teacher', 'student'].map((r) => (
              <option key={r} value={r}>
                {r.toUpperCase()}
              </option>
            ))}
          </select>

          <select
            value={selectedStatusFilter}
            onChange={(e) => setSelectedStatusFilter(e.target.value)}
            className="px-3.5 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs font-bold text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Accounts & Records</option>
            <option value="LINKED">Web Account Linked</option>
            <option value="RECORD_ONLY">University Record Only</option>
            <option value="ACTIVE">Active Only</option>
            <option value="DISABLED">Disabled Only</option>
          </select>
        </div>
      </div>

      {/* Main Users Table */}
      <DataTable
        title={`User Accounts (${filteredUsers.length})`}
        subtitle="Live authentication and authorization roster"
        data={filteredUsers}
        columns={columns}
        searchPlaceholder="Filter user records..."
      />

      {/* Add User Modal with Adaptive Form */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-slate-100 space-y-5 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsAddModalOpen(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-700 p-1.5 rounded-full hover:bg-slate-100 transition-colors"
            >
              <X size={18} />
            </button>

            <div>
              <h3 className="text-lg font-black text-slate-900">Provision User Account</h3>
              <p className="text-xs text-slate-400 font-medium">Create credential and assign role in university hierarchy</p>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Assigned Role</label>
                  <select
                    value={formRole}
                    onChange={(e) => setFormRole(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold text-brand-600 focus:outline-none uppercase"
                  >
                    {allowedRoles.map((r) => (
                      <option key={r} value={r}>
                        {r.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Prof. Ahmed"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500/20 font-medium"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  placeholder="e.g. user@university.edu"
                  value={formEmail}
                  onChange={(e) => setFormEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500/20 font-medium"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1 flex items-center justify-between">
                  <span>Initial Password</span>
                  <span className="text-[10px] text-slate-400">Default: password123</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    value={formPassword}
                    onChange={(e) => setFormPassword(e.target.value)}
                    className="w-full pl-9 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-mono text-xs focus:ring-2 focus:ring-brand-500/20"
                  />
                  <Lock size={14} className="absolute left-3 top-3 text-slate-400 pointer-events-none" />
                </div>
              </div>

              {/* ADAPTIVE FORM FIELDS BASED ON SELECTED ROLE */}
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-3">
                <p className="font-extrabold text-[11px] uppercase tracking-wider text-slate-400">
                  {formRole.toUpperCase()} Scope & Academic Linkage
                </p>

                {formRole === 'dean' && (
                  <div>
                    <label className="font-bold text-slate-700 block mb-1">Faculty Appointment</label>
                    <select
                      value={formFaculty}
                      onChange={(e) => setFormFaculty(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl font-bold text-slate-700"
                    >
                      {faculties.map((f) => (
                        <option key={f.id} value={f.id}>
                          {f.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {(formRole === 'hod' || formRole === 'teacher' || formRole === 'student') && (
                  <div>
                    <label className="font-bold text-slate-700 block mb-1">Department</label>
                    <select
                      value={formDept}
                      onChange={(e) => setFormDept(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl font-bold text-slate-700"
                    >
                      {departments.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {formRole === 'teacher' && (
                  <div>
                    <label className="font-bold text-slate-700 block mb-1">Employee ID Code</label>
                    <input
                      type="text"
                      placeholder="e.g. EMP-CS-005"
                      value={formEmpId}
                      onChange={(e) => setFormEmpId(e.target.value)}
                      className="w-full px-3.5 py-2 bg-white border border-slate-200 rounded-xl font-mono uppercase"
                    />
                  </div>
                )}

                {formRole === 'student' && (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Program</label>
                        <select
                          value={formProgram}
                          onChange={(e) => setFormProgram(e.target.value)}
                          className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl font-bold text-slate-700"
                        >
                          {programs
                            .filter((p) => !formDept || p.departmentId === formDept)
                            .map((p) => (
                              <option key={p.id} value={p.id}>
                                {p.name}
                              </option>
                            ))}
                        </select>
                      </div>
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Roll Number</label>
                        <input
                          type="text"
                          required
                          placeholder="FA24-BCS-001"
                          value={formRollNo}
                          onChange={(e) => setFormRollNo(e.target.value)}
                          className="w-full px-3.5 py-2 bg-white border border-slate-200 rounded-xl font-mono uppercase font-bold text-brand-600"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Semester</label>
                        <select
                          value={formSemester}
                          onChange={(e) => setFormSemester(e.target.value)}
                          className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl font-bold text-slate-700"
                        >
                          {['1', '2', '3', '4', '5', '6', '7', '8'].map((s) => (
                            <option key={s} value={s}>
                              Semester {s}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Section</label>
                        <select
                          value={formSection}
                          onChange={(e) => setFormSection(e.target.value)}
                          className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl font-bold text-slate-700"
                        >
                          <option value="A">Section A</option>
                          <option value="B">Section B</option>
                        </select>
                      </div>
                    </div>
                  </>
                )}

                {formRole === 'vc' && (
                  <p className="text-slate-500 text-xs">Assigned to: Global Tech University (`univ-tech-01`)</p>
                )}

                {formRole === 'admin' && (
                  <p className="text-slate-500 text-xs">Assigned to: Complete System Administration</p>
                )}
              </div>

              <div className="flex items-center gap-3 pt-2">
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
                  {submitting ? 'Creating...' : 'Provision User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
