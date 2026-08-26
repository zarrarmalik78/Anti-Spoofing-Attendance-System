import React, { useEffect, useState } from 'react';
import { collection, query, orderBy, limit, onSnapshot } from 'firebase/firestore';
import { db } from '../firebase/config';
import { Activity, ShieldAlert, CheckCircle, HelpCircle } from 'lucide-react';

interface RecEvent {
  id: string;
  timestamp: number;
  eventType: string;
  studentName?: string;
  cameraId: string;
  confidence: number;
  livenessScore: number;
}

export const LiveMonitoring: React.FC = () => {
  const [events, setEvents] = useState<RecEvent[]>([]);

  useEffect(() => {
    const q = query(
      collection(db, 'recognition_events'),
      orderBy('timestamp', 'desc'),
      limit(20)
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const newEvents: RecEvent[] = [];
      snapshot.forEach((doc) => {
        newEvents.push({ id: doc.id, ...doc.data() } as RecEvent);
      });
      setEvents(newEvents);
    });

    return () => unsubscribe();
  }, []);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'RECOGNIZED':
        return <CheckCircle className="text-green-500" size={24} />;
      case 'SPOOF':
        return <ShieldAlert className="text-red-500" size={24} />;
      default:
        return <HelpCircle className="text-orange-500" size={24} />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="text-primary-600 animate-pulse" />
            Live Security Monitoring
          </h2>
          <p className="text-gray-500 mt-1">Real-time edge recognition events from local cameras</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm text-left text-gray-500">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Time</th>
              <th className="px-6 py-4">Subject</th>
              <th className="px-6 py-4">Event Type</th>
              <th className="px-6 py-4">Camera</th>
              <th className="px-6 py-4">Liveness</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-500">Listening for live events...</td></tr>
            ) : (
              events.map((evt) => (
                <tr key={evt.id} className="border-b hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    {getEventIcon(evt.eventType)}
                  </td>
                  <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                    {new Date(evt.timestamp * 1000).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {evt.studentName || 'Unknown'}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                      evt.eventType === 'RECOGNIZED' ? 'bg-green-100 text-green-800' :
                      evt.eventType === 'SPOOF' ? 'bg-red-100 text-red-800' :
                      'bg-orange-100 text-orange-800'
                    }`}>
                      {evt.eventType}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {evt.cameraId}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-1.5">
                        <div 
                          className={`h-1.5 rounded-full ${evt.livenessScore > 0.8 ? 'bg-green-500' : 'bg-red-500'}`} 
                          style={{ width: `${Math.min(100, Math.max(0, evt.livenessScore * 100))}%` }}
                        ></div>
                      </div>
                      <span className="text-xs">{(evt.livenessScore * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
