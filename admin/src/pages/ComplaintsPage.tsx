import { useState, useCallback } from 'react';
import { Search, CheckCircle } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { useApi, useMutation } from '@/hooks/useApi';
import { getComplaints, updateComplaint, resolveComplaint } from '@/services/complaints';
import type { Complaint, ComplaintPriority, ComplaintStatus } from '@/types';
import { Table, type Column } from '@/components/ui/Table';
import { Badge, getStatusBadgeVariant } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Textarea';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { Card } from '@/components/ui/Card';

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'open', label: 'Open' },
  { value: 'in_review', label: 'In Review' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
];

const priorityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' },
];

export function ComplaintsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  const [resolution, setResolution] = useState('');

  const fetchComplaints = useCallback(
    () => getComplaints({ page, page_size: 10, search, status: statusFilter || undefined }),
    [page, search, statusFilter]
  );

  const { data, loading, refetch } = useApi(fetchComplaints, [page, search, statusFilter]);
  const { mutate: updateMutate } = useMutation(updateComplaint);
  const { mutate: resolveMutate, loading: resolving } = useMutation(resolveComplaint);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  const handleStatusChange = async (id: string, status: ComplaintStatus) => {
    await updateMutate(id, { status });
    refetch();
  };

  const handlePriorityChange = async (id: string, priority: ComplaintPriority) => {
    await updateMutate(id, { priority });
    refetch();
  };

  const handleResolve = async () => {
    if (!selectedComplaint || !resolution.trim()) return;
    const result = await resolveMutate(selectedComplaint.id, resolution);
    if (result) {
      setSelectedComplaint(null);
      setResolution('');
      refetch();
    }
  };

  const columns: Column<Complaint>[] = [
    {
      key: 'id',
      header: 'ID',
      render: (c) => <span className="cell-mono">#{c.id.slice(0, 8)}</span>,
    },
    { key: 'subject', header: 'Subject' },
    { key: 'user_name', header: 'User' },
    {
      key: 'priority',
      header: 'Priority',
      render: (c) => (
        <Badge variant={getStatusBadgeVariant(c.priority)}>
          {c.priority}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (c) => (
        <Badge variant={getStatusBadgeVariant(c.status)} dot>
          {c.status.replace('_', ' ')}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Submitted',
      render: (c) => format(parseISO(c.created_at), 'MMM d, yyyy'),
    },
    {
      key: 'actions',
      header: 'Actions',
      align: 'right',
      render: (c) => (
        <div className="table-actions">
          {c.status !== 'resolved' && c.status !== 'closed' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedComplaint(c)}
              title="Resolve"
            >
              <CheckCircle size={16} />
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="page">
      <div className="page-toolbar">
        <form className="search-form" onSubmit={handleSearch}>
          <Input
            placeholder="Search complaints..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            leftIcon={<Search size={18} />}
          />
          <Select
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as ComplaintStatus | '');
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
          keyExtractor={(c) => c.id}
          loading={loading}
          emptyMessage="No complaints found"
          onRowClick={setSelectedComplaint}
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
        isOpen={!!selectedComplaint}
        onClose={() => {
          setSelectedComplaint(null);
          setResolution('');
        }}
        title="Complaint Details"
        size="lg"
        footer={
          selectedComplaint &&
          selectedComplaint.status !== 'resolved' &&
          selectedComplaint.status !== 'closed' ? (
            <>
              <Button
                variant="outline"
                onClick={() => {
                  setSelectedComplaint(null);
                  setResolution('');
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleResolve} loading={resolving} disabled={!resolution.trim()}>
                Resolve Complaint
              </Button>
            </>
          ) : (
            <Button variant="outline" onClick={() => setSelectedComplaint(null)}>
              Close
            </Button>
          )
        }
      >
        {selectedComplaint && (
          <div className="complaint-detail">
            <div className="complaint-detail-header">
              <h3>{selectedComplaint.subject}</h3>
              <div className="complaint-badges">
                <Badge variant={getStatusBadgeVariant(selectedComplaint.priority)}>
                  {selectedComplaint.priority}
                </Badge>
                <Badge variant={getStatusBadgeVariant(selectedComplaint.status)} dot>
                  {selectedComplaint.status.replace('_', ' ')}
                </Badge>
              </div>
            </div>

            <div className="complaint-meta">
              <div>
                <span className="meta-label">Submitted by</span>
                <span>{selectedComplaint.user_name}</span>
              </div>
              <div>
                <span className="meta-label">Date</span>
                <span>{format(parseISO(selectedComplaint.created_at), 'PPpp')}</span>
              </div>
              {selectedComplaint.ride_id && (
                <div>
                  <span className="meta-label">Related Ride</span>
                  <span className="cell-mono">#{selectedComplaint.ride_id.slice(0, 8)}</span>
                </div>
              )}
            </div>

            <div className="complaint-description">
              <span className="meta-label">Description</span>
              <p>{selectedComplaint.description}</p>
            </div>

            {selectedComplaint.status !== 'resolved' && selectedComplaint.status !== 'closed' && (
              <div className="complaint-actions-form">
                <Select
                  label="Update Status"
                  options={statusOptions.filter((o) => o.value !== '')}
                  value={selectedComplaint.status}
                  onChange={(e) =>
                    handleStatusChange(selectedComplaint.id, e.target.value as ComplaintStatus)
                  }
                />
                <Select
                  label="Priority"
                  options={priorityOptions}
                  value={selectedComplaint.priority}
                  onChange={(e) =>
                    handlePriorityChange(selectedComplaint.id, e.target.value as ComplaintPriority)
                  }
                />
                <Textarea
                  label="Resolution"
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  placeholder="Describe how this complaint was resolved..."
                  rows={3}
                />
              </div>
            )}

            {selectedComplaint.resolution && (
              <div className="complaint-resolution">
                <span className="meta-label">Resolution</span>
                <p>{selectedComplaint.resolution}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
