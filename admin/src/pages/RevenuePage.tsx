import { useState } from 'react';
import { Download, DollarSign, TrendingUp, Car, Percent } from 'lucide-react';
import { useApi } from '@/hooks/useApi';
import { getRevenueAnalytics, exportRevenueReport } from '@/services/revenue';
import { StatCard } from '@/components/charts/StatCard';
import { RevenueChart } from '@/components/charts/RevenueChart';
import { RideStatsChart } from '@/components/charts/RideStatsChart';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { PageLoader } from '@/components/ui/Spinner';

type Period = '7d' | '30d' | '90d' | '1y';

const periodOptions = [
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 90 days' },
  { value: '1y', label: 'Last year' },
];

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
  }).format(value);
}

export function RevenuePage() {
  const [period, setPeriod] = useState<Period>('30d');
  const [exporting, setExporting] = useState(false);

  const { data, loading } = useApi(() => getRevenueAnalytics(period), [period]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await exportRevenueReport(period, 'csv');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `railride-revenue-${period}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Failed to export report');
    } finally {
      setExporting(false);
    }
  };

  if (loading && !data) {
    return <PageLoader />;
  }

  const summary = data?.summary;

  return (
    <div className="page">
      <div className="page-toolbar">
        <Select
          options={periodOptions}
          value={period}
          onChange={(e) => setPeriod(e.target.value as Period)}
        />
        <Button variant="outline" onClick={handleExport} loading={exporting} icon={<Download size={18} />}>
          Export CSV
        </Button>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Revenue"
          value={summary ? formatCurrency(summary.total_revenue) : '—'}
          icon={<DollarSign size={24} />}
          color="blue"
        />
        <StatCard
          title="This Month"
          value={summary ? formatCurrency(summary.month_revenue) : '—'}
          icon={<TrendingUp size={24} />}
          color="green"
        />
        <StatCard
          title="Total Rides"
          value={summary?.total_rides.toLocaleString() ?? '—'}
          icon={<Car size={24} />}
          color="purple"
        />
        <StatCard
          title="Commission Earned"
          value={summary ? formatCurrency(summary.commission_earned) : '—'}
          icon={<Percent size={24} />}
          color="orange"
        />
      </div>

      <div className="revenue-summary-row">
        <Card>
          <div className="revenue-metric">
            <span className="revenue-metric-label">Today's Revenue</span>
            <span className="revenue-metric-value">
              {summary ? formatCurrency(summary.today_revenue) : '—'}
            </span>
          </div>
        </Card>
        <Card>
          <div className="revenue-metric">
            <span className="revenue-metric-label">This Week</span>
            <span className="revenue-metric-value">
              {summary ? formatCurrency(summary.week_revenue) : '—'}
            </span>
          </div>
        </Card>
        <Card>
          <div className="revenue-metric">
            <span className="revenue-metric-label">Average Fare</span>
            <span className="revenue-metric-value">
              {summary ? formatCurrency(summary.average_fare) : '—'}
            </span>
          </div>
        </Card>
      </div>

      <div className="dashboard-charts">
        <Card className="chart-card">
          <CardHeader title="Revenue Trend" subtitle={`Revenue over ${period}`} />
          <RevenueChart data={data?.daily ?? []} height={360} />
        </Card>

        <Card className="chart-card">
          <CardHeader title="Ride Volume" subtitle="Number of rides per day" />
          <RideStatsChart data={data?.daily ?? []} height={360} />
        </Card>
      </div>

      {data?.monthly && data.monthly.length > 0 && (
        <Card className="chart-card">
          <CardHeader title="Monthly Overview" subtitle="Long-term revenue trends" />
          <RevenueChart data={data.monthly} height={300} />
        </Card>
      )}
    </div>
  );
}
