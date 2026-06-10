import { useState, useCallback } from 'react';
import { Plus, Send, Trash2 } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { useApi, useMutation } from '@/hooks/useApi';
import {
  getNotifications,
  createNotification,
  sendNotification,
  deleteNotification,
} from '@/services/notifications';
import type { Notification, NotificationCreate, NotificationTarget } from '@/types';
import { Table, type Column } from '@/components/ui/Table';
import { Badge, getStatusBadgeVariant } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Textarea';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { Card } from '@/components/ui/Card';

const targetOptions = [
  { value: 'all_users', label: 'All Users' },
  { value: 'all_drivers', label: 'All Drivers' },
  { value: 'specific_users', label: 'Specific Users' },
  { value: 'specific_drivers', label: 'Specific Drivers' },
];

const emptyForm: NotificationCreate = {
  title: '',
  message: '',
  target: 'all_users',
};

export function NotificationsPage() {
  const [page, setPage] = useState(1);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [form, setForm] = useState<NotificationCreate>(emptyForm);
  const [formError, setFormError] = useState('');

  const fetchNotifications = useCallback(
    () => getNotifications({ page, page_size: 10 }),
    [page]
  );

  const { data, loading, refetch } = useApi(fetchNotifications, [page]);
  const { mutate: createMutate, loading: creating } = useMutation(createNotification);
  const { mutate: sendMutate } = useMutation(sendNotification);
  const { mutate: deleteMutate } = useMutation(deleteNotification);

  const handleCreate = async () => {
    setFormError('');
    if (!form.title || !form.message) {
      setFormError('Title and message are required');
      return;
    }
    const result = await createMutate(form);
    if (result) {
      setShowCreateModal(false);
      setForm(emptyForm);
      refetch();
    }
  };

  const formatTarget = (target: NotificationTarget): string => {
    return target.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const columns: Column<Notification>[] = [
    { key: 'title', header: 'Title' },
    {
      key: 'message',
      header: 'Message',
      render: (n) => (
        <span className="cell-truncate">{n.message}</span>
      ),
    },
    {
      key: 'target',
      header: 'Target',
      render: (n) => formatTarget(n.target),
    },
    {
      key: 'status',
      header: 'Status',
      render: (n) => (
        <Badge variant={getStatusBadgeVariant(n.status)} dot>
          {n.status}
        </Badge>
      ),
    },
    {
      key: 'recipient_count',
      header: 'Recipients',
      align: 'center',
      render: (n) => n.recipient_count.toLocaleString(),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (n) => format(parseISO(n.created_at), 'MMM d, yyyy h:mm a'),
    },
    {
      key: 'actions',
      header: 'Actions',
      align: 'right',
      render: (n) => (
        <div className="table-actions">
          {n.status === 'draft' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={async () => {
                await sendMutate(n.id);
                refetch();
              }}
              title="Send now"
            >
              <Send size={16} />
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={async () => {
              if (window.confirm('Delete this notification?')) {
                await deleteMutate(n.id);
                refetch();
              }
            }}
            title="Delete"
          >
            <Trash2 size={16} />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="page">
      <div className="page-toolbar">
        <div />
        <Button icon={<Plus size={18} />} onClick={() => setShowCreateModal(true)}>
          New Notification
        </Button>
      </div>

      <Card padding="none">
        <Table
          columns={columns}
          data={data?.items ?? []}
          keyExtractor={(n) => n.id}
          loading={loading}
          emptyMessage="No notifications found"
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
        title="Create Notification"
        footer={
          <>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} loading={creating}>
              Save as Draft
            </Button>
          </>
        }
      >
        {formError && <div className="alert alert-error">{formError}</div>}
        <div className="form-stack">
          <Input
            label="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Notification title"
            required
          />
          <Textarea
            label="Message"
            value={form.message}
            onChange={(e) => setForm({ ...form, message: e.target.value })}
            placeholder="Write your notification message..."
            rows={4}
            required
          />
          <Select
            label="Target Audience"
            options={targetOptions}
            value={form.target}
            onChange={(e) => setForm({ ...form, target: e.target.value as NotificationTarget })}
          />
          <Input
            label="Schedule (optional)"
            type="datetime-local"
            onChange={(e) =>
              setForm({
                ...form,
                scheduled_at: e.target.value ? new Date(e.target.value).toISOString() : undefined,
              })
            }
          />
        </div>
      </Modal>
    </div>
  );
}
