import React from 'react';

interface SegmentedProgressProps {
  percentage: number; // 0 to 100
  totalSegments?: number;
  variant?: 'success' | 'warning' | 'danger' | 'brand';
  showLabel?: boolean;
}

export const SegmentedProgress: React.FC<SegmentedProgressProps> = ({
  percentage,
  totalSegments = 10,
  variant = 'success',
  showLabel = true,
}) => {
  const activeSegments = Math.round((Math.min(100, Math.max(0, percentage)) / 100) * totalSegments);

  const getVariantClass = () => {
    switch (variant) {
      case 'brand':
        return 'bg-brand-600';
      case 'warning':
        return 'bg-amber-500';
      case 'danger':
        return 'bg-rose-500';
      case 'success':
      default:
        return 'bg-emerald-500';
    }
  };

  return (
    <div className="flex items-center gap-3 w-full">
      <div className="flex-1 flex gap-1 items-center">
        {Array.from({ length: totalSegments }).map((_, index) => {
          const isActive = index < activeSegments;
          return (
            <div
              key={index}
              className={`h-2 flex-1 rounded-sm transition-all duration-300 ${
                isActive ? getVariantClass() : 'bg-slate-200'
              }`}
            />
          );
        })}
      </div>
      {showLabel && (
        <span className="text-xs font-bold text-slate-700 w-10 text-right">
          {percentage}%
        </span>
      )}
    </div>
  );
};
