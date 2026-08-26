import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: string;
  trendUp?: boolean;
  avatars?: string[];
  moreAvatarsCount?: number;
  subtitle?: string;
  badge?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  trend,
  trendUp = true,
  avatars,
  moreAvatarsCount,
  subtitle,
  badge,
}) => {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-soft border border-slate-100/80 hover:shadow-soft-lg transition-all duration-300 flex flex-col justify-between relative overflow-hidden group">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="p-3 bg-brand-50 text-brand-600 rounded-xl group-hover:bg-brand-600 group-hover:text-white transition-all duration-300">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</h3>
            <p className="text-2xl font-black text-slate-900 mt-0.5 tracking-tight">{value}</p>
          </div>
        </div>

        {badge && (
          <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-brand-50 text-brand-600 border border-brand-100">
            {badge}
          </span>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-slate-50 flex items-center justify-between gap-2">
        {trend && (
          <div className="flex items-center gap-1.5 text-xs font-semibold">
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold ${
                trendUp ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'
              }`}
            >
              {trendUp ? '↑' : '↓'} {trend}
            </span>
            {subtitle && <span className="text-slate-400 font-normal">{subtitle}</span>}
          </div>
        )}

        {avatars && avatars.length > 0 && (
          <div className="flex items-center -space-x-2 overflow-hidden ml-auto">
            {avatars.slice(0, 3).map((img, i) => (
              <img
                key={i}
                src={img}
                alt="Member"
                className="inline-block h-6 w-6 rounded-full ring-2 ring-white object-cover"
              />
            ))}
            {moreAvatarsCount && moreAvatarsCount > 0 && (
              <span className="inline-flex items-center justify-center h-6 px-1.5 rounded-full ring-2 ring-white bg-slate-100 text-slate-600 text-[10px] font-bold">
                +{moreAvatarsCount} More
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
