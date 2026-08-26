import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/ui/StatCard';
import { Users, BookOpen, UserCheck, Percent } from 'lucide-react';
import { collection, query, where, getDocs } from 'firebase/firestore';
import { db } from '../../firebase/config';

export const TeacherDashboard: React.FC = () => {
  const { profile } = useAuth();
  const [stats, setStats] = useState({
    totalClasses: 0,
    totalStudents: 0,
    todayAttendance: 0,
    attendancePercent: "0%",
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (!profile?.scope?.teacherId && !profile?.scope?.departmentId) return;

      try {
        const teacherId = profile.scope.teacherId || "teacher-ali-01"; // Fallback for demo
        
        const classesRef = collection(db, 'classes');
        const qClasses = query(classesRef, where("teacherId", "==", teacherId));
        const classSnap = await getDocs(qClasses);
        const classCount = classSnap.size;
        const classIds = classSnap.docs.map(d => d.id);

        let totalStudents = 0;
        if (classIds.length > 0) {
          const studentsRef = collection(db, 'students');
          // Firestore array-contains-any has limits, doing a simplified count for demo
          const qStudents = query(studentsRef, where("classIds", "array-contains-any", classIds.slice(0, 10)));
          const studentSnap = await getDocs(qStudents);
          totalStudents = studentSnap.size;
        }

        // Just mocking today's attendance for visual purposes
        const todayAttendance = Math.floor(totalStudents * 0.85);
        const percent = totalStudents > 0 ? Math.round((todayAttendance / totalStudents) * 100) : 0;

        setStats({
          totalClasses: classCount,
          totalStudents,
          todayAttendance,
          attendancePercent: `${percent}%`
        });

      } catch (err) {
        console.error("Failed to fetch teacher stats:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [profile]);

  if (loading) {
    return <div className="flex justify-center p-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Assigned Classes" value={stats.totalClasses} icon={<BookOpen />} />
        <StatCard title="Total Students" value={stats.totalStudents} icon={<Users />} />
        <StatCard title="Today's Check-ins" value={stats.todayAttendance} icon={<UserCheck />} />
        <StatCard title="Avg Attendance" value={stats.attendancePercent} icon={<Percent />} trend="Above target" trendUp={true} />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mt-8">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Today's Class Attendance</h3>
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">View All Reports</button>
        </div>
        <div className="p-12 text-center text-gray-500">
          <CalendarIcon className="mx-auto h-12 w-12 text-gray-300 mb-4" />
          <p>No classes scheduled for today.</p>
        </div>
      </div>
    </div>
  );
};

// Simple icon for empty state
function CalendarIcon(props: any) {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  );
}
