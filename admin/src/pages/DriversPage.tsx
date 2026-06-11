import { useState, useCallback } from 'react';
import { Search, Plus, CheckCircle, UserX, Trash2, Star } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { useApi, useMutation } from '@/hooks/useApi';
import {
  getDrivers,
  createDriver,
  approveDriver,
  suspendDriver,
  deleteDriver,
} from '@/services/drivers';
import type { Driver, DriverCreate, DriverStatus } from '@/types';
import { Table, type Column } from '@/components/ui/Table';
import { Badge, getStatusBadgeVariant } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { Card } from '@/components/ui/Card';

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'online', label: 'Online' },
  { value: 'offline', label: 'Offline' },
  { value: 'on_ride', label: 'On Ride' },
  { value: 'pending_approval', label: 'Pending Approval' },
  { value: 'suspended', label: 'Suspended' },
];

const emptyForm: DriverCreate = {
  email: '',
  full_name: '',
  phone: '',
  license_number: '',
  vehicle_model: '',
  vehicle_plate: '',
  password: '',
};

export function DriversPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [form, setForm] = useState<DriverCreate>(emptyForm);
  const [formError, setFormError] = useState('');

  const fetchDrivers = useCallback(
    () => getDrivers({ page, page_size: 10, search, status: statusFilter || undefined }),
    [page, search, statusFilter]
  );

  const { data, loading, refetch } = useApi(fetchDrivers, [page, search, statusFilter]);
  console.log(data,"drivers data");
  const { mutate: createMutate, loading: creating } = useMutation(createDriver);
  const { mutate: approveMutate } = useMutation(approveDriver);
  const { mutate: suspendMutate } = useMutation(suspendDriver);
  const { mutate: deleteMutate } = useMutation(deleteDriver);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  const handleCreate = async () => {
    setFormError('');
    if (!form.email || !form.full_name || !form.license_number || !form.password) {
      setFormError('Please fill in all required fields');
      return;
    }
    const result = await createMutate(form);
    if (result) {
      setShowCreateModal(false);
      setForm(emptyForm);
      refetch();
    }
  };

  const columns: Column<Driver>[] = [
    {
      key: 'full_name',
      header: 'Driver',
      render: (driver) => (
        <div className="cell-user">
          <span className="cell-user-name">{driver.full_name}</span>
          <span className="cell-user-email">{driver.email}</span>
        </div>
      ),
    },
    {
      key: 'vehicle',
      header: 'Vehicle',
      render: (driver) => (
        <div>
          <span>{driver.vehicle_model}</span>
          <span className="cell-muted"> · {driver.vehicle_plate}</span>
        </div>
      ),
    },
    // {
    //   key: 'status',
    //   header: 'Status',
    //   render: (driver) => (
    //     <Badge variant={getStatusBadgeVariant(driver.status)} dot>
    //       {driver.status.replace('_', ' ')}
    //     </Badge>
    //   ),
    // },
    {
      key: 'rating',
      header: 'Rating',
      render: (driver) => (
        <span className="cell-rating">
          <Star size={14} fill="#f59e0b" stroke="#f59e0b" />
          {driver.rating.toFixed(1)}
        </span>
      ),
    },
    { key: 'total_rides', header: 'Rides', align: 'center' },
    // {
    //   key: 'created_at',
    //   header: 'Joined',
    //   render: (driver) => format(parseISO(driver.created_at), 'MMM d, yyyy'),
    // },
    {
      key: 'actions',
      header: 'Actions',
      align: 'right',
      render: (driver) => (
        <div className="table-actions">
          {driver.status === 'pending_approval' && (
            <Button variant="ghost" size="sm" onClick={async () => { await approveMutate(driver.id); refetch(); }} title="Approve">
              <CheckCircle size={16} />
            </Button>
          )}
          {driver.status !== 'suspended' && (
            <Button variant="ghost" size="sm" onClick={async () => { await suspendMutate(driver.id); refetch(); }} title="Suspend">
              <UserX size={16} />
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={async () => {
            if (window.confirm('Delete this driver?')) {
              await deleteMutate(driver.id);
              refetch();
            }
          }} title="Delete">
            <Trash2 size={16} />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="page">
      <div className="page-toolbar">
        <form className="search-form" onSubmit={handleSearch}>
          <Input
            placeholder="Search drivers..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            leftIcon={<Search size={18} />}
          />
          <Select
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as DriverStatus | '');
              setPage(1);
            }}
          />
          <Button type="submit" variant="secondary">
            Search
          </Button>
        </form>
        <Button icon={<Plus size={18} />} onClick={() => setShowCreateModal(true)}>
          Add Driver
        </Button>
      </div>

      <Card padding="none">
        <Table
          columns={columns}
          data={data ?? []}
          keyExtractor={(d) => d.id}
          loading={loading}
          emptyMessage="No drivers found"
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

      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Register New Driver"
        size="lg"
        footer={
          <>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} loading={creating}>
              Register Driver
            </Button>
          </>
        }
      >
        {formError && <div className="alert alert-error">{formError}</div>}
        <div className="form-grid">
          <Input label="Full Name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
          <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input label="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          <Input label="License Number" value={form.license_number} onChange={(e) => setForm({ ...form, license_number: e.target.value })} required />
          <Input label="Vehicle Model" value={form.vehicle_model} onChange={(e) => setForm({ ...form, vehicle_model: e.target.value })} />
          <Input label="Vehicle Plate" value={form.vehicle_plate} onChange={(e) => setForm({ ...form, vehicle_plate: e.target.value })} />
          <Input label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        </div>
      </Modal>
    </div>
  );
}
