import type { ReactNode } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  trend?: number;
  trendLabel?: string;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

const colorClasses = {
  blue: 'stat-card-blue',
  green: 'stat-card-green',
  purple: 'stat-card-purple',
  orange: 'stat-card-orange',
  red: 'stat-card-red',
};

export function StatCard({
  title,
  value,
  icon,
  trend,
  trendLabel,
  color = 'blue',
}: StatCardProps) {
  const isPositive = trend !== undefined && trend >= 0;

  return (
    <div className={`stat-card ${colorClasses[color]}`}>
      <div className="stat-card-content">
        <span className="stat-card-title">{title}</span>
        <span className="stat-card-value">{value}</span>
        {trend !== undefined && (
          <div className={`stat-card-trend ${isPositive ? 'positive' : 'negative'}`}>
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>
              {isPositive ? '+' : ''}
              {trend}%
            </span>
            {trendLabel && <span className="stat-card-trend-label">{trendLabel}</span>}
          </div>
        )}
      </div>
      <div className="stat-card-icon">{icon}</div>
    </div>
  );
}
