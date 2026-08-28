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
    <div className="bg-white rounded-3xl p-5 shadow-soft border border-slate-200/60 hover:border-brand-300/80 hover:shadow-soft-xl transition-all duration-300 flex flex-col justify-between relative overflow-hidden group hover:-translate-y-1">
      {/* Background Subtle Mesh Spot */}
      <div className="absolute -top-12 -right-12 w-28 h-28 bg-gradient-to-br from-brand-50 to-indigo-50/50 rounded-full blur-2xl group-hover:from-brand-100 group-hover:to-indigo-100 transition-all duration-500 pointer-events-none" />

      <div className="flex items-start justify-between gap-4 relative z-10">
        <div className="flex items-center gap-3.5">
          {icon && (
            <div className="p-3.5 bg-gradient-to-br from-brand-50 to-indigo-50/80 text-brand-600 rounded-2xl group-hover:from-brand-600 group-hover:to-indigo-600 group-hover:text-white shadow-xs group-hover:shadow-md group-hover:shadow-brand-500/20 transition-all duration-300">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">{title}</h3>
            <p className="text-2xl font-black text-slate-900 mt-0.5 tracking-tight group-hover:text-brand-950 transition-colors">{value}</p>
          </div>
        </div>

        {badge && (
          <span className="text-[10px] font-extrabold px-2.5 py-1 rounded-full bg-brand-50 text-brand-700 border border-brand-200/60 shadow-2xs">
            {badge}
          </span>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100/80 flex items-center justify-between gap-2 relative z-10">
        {trend ? (
          <div className="flex items-center gap-1.5 text-xs font-semibold">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wide border ${
                trendUp
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200/60'
                  : 'bg-rose-50 text-rose-700 border-rose-200/60'
              }`}
            >
              {trendUp ? '↑' : '↓'} {trend}
            </span>
            {subtitle && <span className="text-slate-400 font-medium text-[11px]">{subtitle}</span>}
          </div>
        ) : (
          subtitle && <span className="text-slate-400 font-medium text-[11px]">{subtitle}</span>
        )}

        {avatars && avatars.length > 0 && (
          <div className="flex items-center -space-x-2 overflow-hidden ml-auto">
            {avatars.slice(0, 3).map((img, i) => (
              <img
                key={i}
                src={img}
                alt="Member"
                className="inline-block h-6 w-6 rounded-full ring-2 ring-white object-cover shadow-2xs"
              />
            ))}
            {moreAvatarsCount && moreAvatarsCount > 0 && (
              <span className="inline-flex items-center justify-center h-6 px-2 rounded-full ring-2 ring-white bg-slate-100 text-slate-700 text-[10px] font-extrabold shadow-2xs">
                +{moreAvatarsCount}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
