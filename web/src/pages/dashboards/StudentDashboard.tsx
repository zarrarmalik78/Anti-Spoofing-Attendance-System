import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { StatCard } from '../../components/ui/StatCard';
import { BookOpen, CalendarCheck, Clock, Percent } from 'lucide-react';
import { collection, query, where, getDocs } from 'firebase/firestore';
import { db } from '../../firebase/config';

export const StudentDashboard: React.FC = () => {
  const { profile } = useAuth();
  const [stats, setStats] = useState({
    classesAttended: 0,
    totalClasses: 0,
    attendancePercent: "0%",
  });
  const [recentAttendance, setRecentAttendance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (!profile?.scope?.studentId) return;

      try {
        const studentId = profile.scope.studentId;
        
        // Fetch Attendance
        const attRef = collection(db, 'attendance');
        const q = query(attRef, where("studentId", "==", studentId));
        const snapshot = await getDocs(q);
        
        const records = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        
        // Fake "Total Classes" based on enrolled classIds
        const totalClasses = (profile.classIds?.length || 0) * 20 || 30; // Mock calculation
        const classesAttended = records.length;
        const percentage = totalClasses > 0 ? Math.round((classesAttended / totalClasses) * 100) : 0;

        setStats({
          classesAttended,
          totalClasses,
          attendancePercent: `${percentage}%`
        });

        // Sort by timestamp
        records.sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        setRecentAttendance(records.slice(0, 5));
        
      } catch (err) {
        console.error("Failed to fetch student stats:", err);
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
        <StatCard title="Overall Attendance" value={stats.attendancePercent} icon={<Percent />} trend="Looking good" trendUp={true} />
        <StatCard title="Classes Attended" value={stats.classesAttended} icon={<CalendarCheck />} />
        <StatCard title="Total Classes" value={stats.totalClasses} icon={<BookOpen />} />
        <StatCard title="Missed Classes" value={stats.totalClasses - stats.classesAttended} icon={<Clock />} trend="Needs improvement" trendUp={false} />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Recent Attendance</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50">
              <tr>
                <th className="px-6 py-3">Date / Time</th>
                <th className="px-6 py-3">Course / Class</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Method</th>
              </tr>
            </thead>
            <tbody>
              {recentAttendance.length === 0 ? (
                <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-500">No recent attendance found.</td></tr>
              ) : (
                recentAttendance.map(record => (
                  <tr key={record.id} className="bg-white border-b hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                      {new Date(record.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      {record.courseId || "General Check-in"}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Present
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-500">
                      Face ID ({record.confidence > 0.8 ? 'High' : 'Low'} Conf)
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
