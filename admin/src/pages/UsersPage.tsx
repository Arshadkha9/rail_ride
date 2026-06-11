import { useState, useCallback } from 'react';
import { Search, Plus, UserX, UserCheck, Trash2 } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { useApi, useMutation } from '@/hooks/useApi';
import {
  getUsers,
  createUser,
  suspendUser,
  activateUser,
  deleteUser,
} from '@/services/users';
import type { User, UserCreate, UserStatus } from '@/types';
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
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'suspended', label: 'Suspended' },
  { value: 'pending', label: 'Pending' },
];

const emptyForm: UserCreate = {
  email: '',
  full_name: '',
  phone: '',
  password: '',
};

export function UsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [form, setForm] = useState<UserCreate>(emptyForm);
  const [formError, setFormError] = useState('');

  const fetchUsers = useCallback(
    () => getUsers({ page, page_size: 10, search, status: statusFilter || undefined }),
    [page, search, statusFilter]
  );

  const { data, loading, refetch } = useApi(fetchUsers, [page, search, statusFilter]);
  const { mutate: createUserMutate, loading: creating } = useMutation(createUser);
  const { mutate: suspendMutate } = useMutation(suspendUser);
  const { mutate: activateMutate } = useMutation(activateUser);
  const { mutate: deleteMutate } = useMutation(deleteUser);
  console.log(data)
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  const handleCreate = async () => {
    setFormError('');
    if (!form.email || !form.full_name || !form.password) {
      setFormError('Please fill in all required fields');
      return;
    }
    const result = await createUserMutate(form);
    if (result) {
      setShowCreateModal(false);
      setForm(emptyForm);
      refetch();
    }
  };

  const handleSuspend = async (id: string) => {
    await suspendMutate(id);
    refetch();
  };

  const handleActivate = async (id: string) => {
    await activateMutate(id);
    refetch();
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      await deleteMutate(id);
      refetch();
    }
  };

  const columns: Column<User>[] = [
    {
      key: 'full_name',
      header: 'Name',
      render: (user) => (
        <div className="cell-user">
          <span className="cell-user-name">{user.full_name}</span>
          <span className="cell-user-email">{user.email}</span>
        </div>
      ),
    },
    { key: 'mobile', header: 'Phone' },
    {
      key: 'is_active',
      header: 'Status',
      render: (user) => (
        <Badge variant={getStatusBadgeVariant(user.is_active ?'active':'inactive')} dot>
          {user.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    { key: 'total_rides', header: 'Rides', align: 'center' },
    {
      key: 'created_at',
      header: 'Joined',
      render: (user) => format(parseISO(user.created_at), 'MMM d, yyyy'),
    },
    {
      key: 'actions',
      header: 'Actions',
      align: 'right',
      render: (user) => (
        <div className="table-actions">
          {user.status === 'suspended' ? (
            <Button variant="ghost" size="sm" onClick={() => handleActivate(user.id)} title="Activate">
              <UserCheck size={16} />
            </Button>
          ) : (
            <Button variant="ghost" size="sm" onClick={() => handleSuspend(user.id)} title="Suspend">
              <UserX size={16} />
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={() => handleDelete(user.id)} title="Delete">
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
            placeholder="Search users..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            leftIcon={<Search size={18} />}
          />
          <Select
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as UserStatus | '');
              setPage(1);
            }}
          />
          <Button type="submit" variant="secondary">
            Search
          </Button>
        </form>
        <Button icon={<Plus size={18} />} onClick={() => setShowCreateModal(true)}>
          Add User
        </Button>
      </div>

      <Card padding="none">
        <Table
          columns={columns}
          data={data ?? []}
          keyExtractor={(u) => u.id}
          loading={loading}
          emptyMessage="No users found"
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
        title="Create New User"
        footer={
          <>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} loading={creating}>
              Create User
            </Button>
          </>
        }
      >
        {formError && <div className="alert alert-error">{formError}</div>}
        <div className="form-grid">
          <Input
            label="Full Name"
            value={form.full_name}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            required
          />
          <Input
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <Input
            label="Phone"
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
          />
          <Input
            label="Password"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
        </div>
      </Modal>
    </div>
  );
}
