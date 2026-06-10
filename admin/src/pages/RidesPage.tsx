import { useState, useCallback, useEffect } from 'react';
import { Search, RefreshCw } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { useApi } from '@/hooks/useApi';
import { getRides, getLiveRides } from '@/services/rides';
import type { LiveRide, Ride, RideStatus } from '@/types';
import { Table, type Column } from '@/components/ui/Table';
import { Badge, getStatusBadgeVariant } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Pagination } from '@/components/ui/Pagination';
import { Card, CardHeader } from '@/components/ui/Card';
import { LiveMap } from '@/components/rides/LiveMap';

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'requested', label: 'Requested' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

export function RidesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [selectedRideId, setSelectedRideId] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchRides = useCallback(
    () => getRides({ page, page_size: 10, search, status: statusFilter || undefined }),
    [page, search, statusFilter]
  );

  const { data, loading, refetch } = useApi(fetchRides, [page, search, statusFilter]);
  const { data: liveRides, refetch: refetchLive } = useApi(getLiveRides, [], true);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      refetchLive();
    }, 15000);
    return () => clearInterval(interval);
  }, [autoRefresh, refetchLive]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  const handleRefresh = () => {
    refetch();
    refetchLive();
  };

  const columns: Column<Ride>[] = [
    {
      key: 'id',
      header: 'Ride ID',
      render: (ride) => <span className="cell-mono">#{ride.id.slice(0, 8)}</span>,
    },
    { key: 'user_name', header: 'Passenger' },
    {
      key: 'driver_name',
      header: 'Driver',
      render: (ride) => ride.driver_name ?? '—',
    },
    {
      key: 'pickup',
      header: 'Route',
      render: (ride) => (
        <div className="cell-route">
          <span>{ride.pickup.address}</span>
          <span className="cell-route-arrow">→</span>
          <span>{ride.dropoff.address}</span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (ride) => (
        <Badge variant={getStatusBadgeVariant(ride.status)} dot>
          {ride.status.replace('_', ' ')}
        </Badge>
      ),
    },
    {
      key: 'fare',
      header: 'Fare',
      align: 'right',
      render: (ride) => `$${ride.fare.toFixed(2)}`,
    },
    {
      key: 'created_at',
      header: 'Time',
      render: (ride) => format(parseISO(ride.created_at), 'MMM d, h:mm a'),
    },
  ];

  return (
    <div className="page">
      <Card className="rides-map-card">
        <CardHeader
          title="Live Ride Monitoring"
          subtitle="Real-time tracking of active rides"
          action={
            <div className="rides-map-actions">
              <label className="auto-refresh-toggle">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
                Auto-refresh
              </label>
              <Button variant="outline" size="sm" onClick={handleRefresh}>
                <RefreshCw size={16} />
                Refresh
              </Button>
            </div>
          }
        />
        <LiveMap
          rides={liveRides ?? []}
          selectedRideId={selectedRideId}
          onSelectRide={(ride: LiveRide) => setSelectedRideId(ride.id)}
        />
      </Card>

      <div className="page-toolbar">
        <form className="search-form" onSubmit={handleSearch}>
          <Input
            placeholder="Search rides..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            leftIcon={<Search size={18} />}
          />
          <Select
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as RideStatus | '');
              setPage(1);
            }}
          />
          <Button type="submit" variant="secondary">
            Search
          </Button>
        </form>
      </div>

      <Card padding="none">
        <Table
          columns={columns}
          data={data?.items ?? []}
          keyExtractor={(r) => r.id}
          loading={loading}
          emptyMessage="No rides found"
          onRowClick={(ride) => setSelectedRideId(ride.id)}
        />
        {data && (
          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            total={data.total}
            pageSize={data.page_size}
            onPageChange={setPage}
          />
        )}
      </Card>
    </div>
  );
}
