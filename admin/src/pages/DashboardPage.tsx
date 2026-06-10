import { Users, Car, MapPin, DollarSign, MessageSquareWarning, Activity } from 'lucide-react';
import { useApi } from '@/hooks/useApi';
import { getDashboardStats } from '@/services/rides';
import { getRevenueAnalytics } from '@/services/revenue';
import { StatCard } from '@/components/charts/StatCard';
import { RevenueChart } from '@/components/charts/RevenueChart';
import { RideStatsChart } from '@/components/charts/RideStatsChart';
import { Card, CardHeader } from '@/components/ui/Card';
import { PageLoader } from '@/components/ui/Spinner';

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
  }).format(value);
}

export function DashboardPage() {
  const { data: stats, loading: statsLoading } = useApi(getDashboardStats);
  const { data: revenue, loading: revenueLoading } = useApi(() => getRevenueAnalytics('7d'));

  if (statsLoading && !stats) {
    return <PageLoader />;
  }

  return (
    <div className="page">
      <div className="stats-grid">
        <StatCard
          title="Total Users"
          value={stats?.total_users.toLocaleString() ?? '—'}
          icon={<Users size={24} />}
          color="blue"
        />
        <StatCard
          title="Total Drivers"
          value={stats?.total_drivers.toLocaleString() ?? '—'}
          icon={<Car size={24} />}
          color="purple"
        />
        <StatCard
          title="Active Rides"
          value={stats?.active_rides ?? '—'}
          icon={<MapPin size={24} />}
          color="green"
        />
        <StatCard
          title="Today's Revenue"
          value={stats ? formatCurrency(stats.today_revenue) : '—'}
          icon={<DollarSign size={24} />}
          color="orange"
        />
        <StatCard
          title="Online Drivers"
          value={stats?.online_drivers ?? '—'}
          icon={<Activity size={24} />}
          color="green"
        />
        <StatCard
          title="Pending Complaints"
          value={stats?.pending_complaints ?? '—'}
          icon={<MessageSquareWarning size={24} />}
          color="red"
        />
      </div>

      <div className="dashboard-charts">
        <Card className="chart-card">
          <CardHeader title="Revenue (Last 7 Days)" subtitle="Daily revenue trends" />
          {revenueLoading ? (
            <PageLoader />
          ) : (
            <RevenueChart data={revenue?.daily ?? []} />
          )}
        </Card>

        <Card className="chart-card">
          <CardHeader title="Ride Volume" subtitle="Daily completed rides" />
          {revenueLoading ? (
            <PageLoader />
          ) : (
            <RideStatsChart data={revenue?.daily ?? []} />
          )}
        </Card>
      </div>
    </div>
  );
}
