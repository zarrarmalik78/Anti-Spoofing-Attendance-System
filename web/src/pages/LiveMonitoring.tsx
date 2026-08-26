import React, { useEffect, useState } from 'react';
import { collection, query, orderBy, limit, onSnapshot } from 'firebase/firestore';
import { db } from '../firebase/config';
import {
  ShieldAlert,
  CheckCircle,
  HelpCircle,
  Camera,
  Search,
  Eye,
  Radio,
  Clock,
  Laptop
} from 'lucide-react';
import { SegmentedProgress } from '../components/ui/SegmentedProgress';

interface RecEvent {
  id: string;
  timestamp: number;
  eventType: string;
  studentName?: string;
  studentId?: string;
  cameraId: string;
  deviceId?: string;
  confidence: number;
  livenessScore: number;
  avatar?: string;
}

export const LiveMonitoring: React.FC = () => {
  const [events, setEvents] = useState<RecEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<RecEvent | null>(null);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<string>('ALL');

  useEffect(() => {
    const q = query(collection(db, 'recognition_events'), orderBy('timestamp', 'desc'), limit(30));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const newEvents: RecEvent[] = [];
      snapshot.forEach((doc) => {
        newEvents.push({ id: doc.id, ...doc.data() } as RecEvent);
      });

      if (newEvents.length === 0) {
        // Fallback rich demo events if DB has not fired webcam yet
        const mockEvents: RecEvent[] = [
          {
            id: 'evt-1',
            timestamp: Math.floor(Date.now() / 1000),
            eventType: 'RECOGNIZED',
            studentName: 'Ali Khan',
            studentId: 'FA23-BCS-001',
            cameraId: 'WEBCAM-01',
            deviceId: 'LAPTOP-01',
            confidence: 0.94,
            livenessScore: 0.98,
            avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
          },
          {
            id: 'evt-2',
            timestamp: Math.floor(Date.now() / 1000) - 45,
            eventType: 'SPOOF',
            studentName: 'Unverified Photo Target',
            studentId: 'N/A',
            cameraId: 'WEBCAM-01',
            deviceId: 'LAPTOP-01',
            confidence: 0.22,
            livenessScore: 0.14,
          },
          {
            id: 'evt-3',
            timestamp: Math.floor(Date.now() / 1000) - 120,
            eventType: 'RECOGNIZED',
            studentName: 'Sara Ahmed',
            studentId: 'FA23-BCS-008',
            cameraId: 'WEBCAM-01',
            deviceId: 'LAPTOP-01',
            confidence: 0.91,
            livenessScore: 0.95,
            avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80',
          },
          {
            id: 'evt-4',
            timestamp: Math.floor(Date.now() / 1000) - 240,
            eventType: 'UNKNOWN',
            studentName: 'Visitor / Unregistered',
            studentId: 'UNREGISTERED',
            cameraId: 'WEBCAM-01',
            deviceId: 'LAPTOP-01',
            confidence: 0.38,
            livenessScore: 0.92,
          },
        ];
        setEvents(mockEvents);
        setSelectedEvent(mockEvents[0]);
      } else {
        setEvents(newEvents);
        setSelectedEvent((prev) => prev || newEvents[0]);
      }
    });

    return () => unsubscribe();
  }, []);

  const filteredEvents = events.filter((evt) => {
    const matchesSearch =
      !search ||
      evt.studentName?.toLowerCase().includes(search.toLowerCase()) ||
      evt.cameraId.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filterType === 'ALL' || evt.eventType === filterType;
    return matchesSearch && matchesFilter;
  });

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'RECOGNIZED':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-100">
            <CheckCircle size={12} /> Verified
          </span>
        );
      case 'SPOOF':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-100">
            <ShieldAlert size={12} /> Spoof Blocked
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-100">
            <HelpCircle size={12} /> Unknown
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 flex items-center gap-2.5">
            <Radio className="text-rose-500 animate-pulse" size={24} />
            Live Security & Recognition Console
          </h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Real-time biometric validation and anti-spoofing telemetry stream
          </p>
        </div>

        {/* Live Stream Indicators */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-100 text-emerald-700 px-3 py-1.5 rounded-xl text-xs font-bold shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span>Edge Stream Active</span>
          </div>
          <span className="bg-slate-100 text-slate-600 px-3 py-1.5 rounded-xl text-xs font-mono font-bold">
            30 FPS • WEBCAM-01
          </span>
        </div>
      </div>

      {/* Split Pane Activity Console (Matching Image 1 "Message Center" style) */}
      <div className="bg-white rounded-3xl shadow-soft border border-slate-100 overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[640px]">
        {/* Left Pane: Live Stream Event Feed (Col 5) */}
        <div className="lg:col-span-5 border-r border-slate-100 flex flex-col h-full bg-slate-50/30">
          {/* Feed Filter Bar */}
          <div className="p-4 border-b border-slate-100 space-y-3 bg-white">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder="Search live detections..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-3.5 pr-8 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
                <Search size={14} className="absolute right-3 top-2.5 text-slate-400 pointer-events-none" />
              </div>
            </div>

            {/* Filter Pills */}
            <div className="flex items-center gap-2">
              {['ALL', 'RECOGNIZED', 'SPOOF', 'UNKNOWN'].map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-3 py-1 rounded-lg text-[10px] font-bold uppercase transition-all ${
                    filterType === type
                      ? 'bg-brand-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Event Stream List */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100 p-2">
            {filteredEvents.length === 0 ? (
              <div className="p-12 text-center text-slate-400 text-xs font-medium">
                No events matching filter. Waiting for webcam stream...
              </div>
            ) : (
              filteredEvents.map((evt) => {
                const isSelected = selectedEvent?.id === evt.id;
                return (
                  <div
                    key={evt.id}
                    onClick={() => setSelectedEvent(evt)}
                    className={`p-3.5 rounded-2xl cursor-pointer transition-all duration-200 mb-1.5 flex items-start gap-3.5 ${
                      isSelected
                        ? 'bg-white shadow-soft border border-slate-100 ring-1 ring-brand-500/20'
                        : 'hover:bg-white hover:shadow-2xs'
                    }`}
                  >
                    {/* Avatar / Detection Preview */}
                    <div className="relative shrink-0">
                      {evt.avatar ? (
                        <img
                          src={evt.avatar}
                          alt={evt.studentName}
                          className="w-11 h-11 rounded-full object-cover ring-2 ring-slate-100"
                        />
                      ) : evt.eventType === 'SPOOF' ? (
                        <div className="w-11 h-11 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
                          <ShieldAlert size={22} />
                        </div>
                      ) : (
                        <div className="w-11 h-11 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center font-bold">
                          <HelpCircle size={22} />
                        </div>
                      )}
                      <span
                        className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full ring-2 ring-white ${
                          evt.eventType === 'RECOGNIZED'
                            ? 'bg-emerald-500'
                            : evt.eventType === 'SPOOF'
                            ? 'bg-rose-500'
                            : 'bg-amber-500'
                        }`}
                      ></span>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-1">
                        <h4 className="text-xs font-bold text-slate-900 truncate">
                          {evt.studentName || 'Unknown Subject'}
                        </h4>
                        <span className="text-[10px] text-slate-400 font-mono shrink-0">
                          {new Date(evt.timestamp * 1000).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                          })}
                        </span>
                      </div>

                      <div className="flex items-center justify-between mt-1">
                        <p className="text-[11px] text-slate-500 truncate">
                          {evt.cameraId} • Liveness: {(evt.livenessScore * 100).toFixed(0)}%
                        </p>
                        {getEventBadge(evt.eventType)}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Pane: Detailed Telemetry & Biometrics Card (Col 7, Image 1 style) */}
        <div className="lg:col-span-7 flex flex-col h-full bg-white p-8 overflow-y-auto">
          {selectedEvent ? (
            <div className="space-y-6">
              {/* Card Header */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-6">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    {selectedEvent.avatar ? (
                      <img
                        src={selectedEvent.avatar}
                        alt={selectedEvent.studentName}
                        className="w-16 h-16 rounded-2xl object-cover ring-4 ring-slate-50 shadow-md"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center font-black text-xl shadow-md">
                        {selectedEvent.eventType === 'SPOOF' ? <ShieldAlert size={32} /> : <Eye size={32} />}
                      </div>
                    )}
                  </div>
                  <div>
                    <h3 className="text-lg font-black text-slate-900">{selectedEvent.studentName || 'Unregistered Person'}</h3>
                    <p className="text-xs text-slate-400 font-medium">
                      Roll No: {selectedEvent.studentId || 'N/A'} • Camera: {selectedEvent.cameraId}
                    </p>
                  </div>
                </div>

                <div>{getEventBadge(selectedEvent.eventType)}</div>
              </div>

              {/* Biometrics Inspection Card (Image 1 appointment/meeting card style) */}
              <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100/80 space-y-5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    AI Inference Diagnostics
                  </h4>
                  <span className="text-[10px] font-mono text-slate-400 font-bold">
                    ID: {selectedEvent.id}
                  </span>
                </div>

                {/* ArcFace Recognition Confidence */}
                <div>
                  <div className="flex justify-between items-center text-xs font-bold text-slate-700 mb-1.5">
                    <span>ArcFace Embedding Cosine Similarity</span>
                    <span className="text-brand-600">{(selectedEvent.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <SegmentedProgress
                    percentage={Math.round(selectedEvent.confidence * 100)}
                    variant={selectedEvent.confidence > 0.8 ? 'brand' : 'danger'}
                  />
                </div>

                {/* MiniFASNet Liveness Score */}
                <div>
                  <div className="flex justify-between items-center text-xs font-bold text-slate-700 mb-1.5">
                    <span>MiniFASNet Liveness & Anti-Spoofing</span>
                    <span className={selectedEvent.livenessScore > 0.8 ? 'text-emerald-600' : 'text-rose-600'}>
                      {(selectedEvent.livenessScore * 100).toFixed(1)}%
                    </span>
                  </div>
                  <SegmentedProgress
                    percentage={Math.round(selectedEvent.livenessScore * 100)}
                    variant={selectedEvent.livenessScore > 0.8 ? 'success' : 'danger'}
                  />
                </div>
              </div>

              {/* Hardware & Session Meta */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-white text-slate-700 shadow-2xs">
                    <Laptop size={18} />
                  </div>
                  <div>
                    <p className="text-slate-400 text-[11px] font-medium">Edge Device</p>
                    <p className="font-bold text-slate-800">{selectedEvent.deviceId || 'LAPTOP-01'}</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-white text-slate-700 shadow-2xs">
                    <Clock size={18} />
                  </div>
                  <div>
                    <p className="text-slate-400 text-[11px] font-medium">Capture Timestamp</p>
                    <p className="font-bold text-slate-800">
                      {new Date(selectedEvent.timestamp * 1000).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-slate-100 flex items-center gap-3">
                <button
                  onClick={() => alert(`Confirmed attendance record for ${selectedEvent.studentName}`)}
                  className="flex-1 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm shadow-brand-500/20"
                >
                  Confirm & Mark Present
                </button>
                <button
                  onClick={() => alert(`Flagged record ${selectedEvent.id} for manual administrative review.`)}
                  className="px-5 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all"
                >
                  Flag For Review
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center text-slate-400">
              <Camera size={48} className="text-slate-200 mb-3" />
              <p className="font-bold text-sm text-slate-600">No detection selected</p>
              <p className="text-xs text-slate-400 mt-1">Select an event from the stream on the left to inspect</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
