import type { ReactNode } from 'react';

type BadgeVariant =
  | 'default'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'purple';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  dot?: boolean;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'badge-default',
  success: 'badge-success',
  warning: 'badge-warning',
  danger: 'badge-danger',
  info: 'badge-info',
  purple: 'badge-purple',
};

export function Badge({ children, variant = 'default', dot = false }: BadgeProps) {
  return (
    <span className={`badge ${variantClasses[variant]}`}>
      {dot && <span className="badge-dot" />}
      {children}
    </span>
  );
}

export function getStatusBadgeVariant(
  status: string
): BadgeVariant {
  const statusMap: Record<string, BadgeVariant> = {
    active: 'success',
    online: 'success',
    completed: 'success',
    resolved: 'success',
    sent: 'success',
    closed: 'default',
    inactive: 'default',
    offline: 'default',
    draft: 'default',
    pending: 'warning',
    pending_approval: 'warning',
    in_review: 'warning',
    scheduled: 'info',
    on_ride: 'info',
    in_progress: 'info',
    accepted: 'info',
    requested: 'purple',
    suspended: 'danger',
    cancelled: 'danger',
    failed: 'danger',
    open: 'danger',
    urgent: 'danger',
    high: 'danger',
    medium: 'warning',
    low: 'default',
  };
  return statusMap[status] ?? 'default';
}
