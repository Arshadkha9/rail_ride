import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Car,
  MapPin,
  DollarSign,
  Bell,
  MessageSquareWarning,
  Train,
  X,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/users', icon: Users, label: 'Users' },
  { to: '/drivers', icon: Car, label: 'Drivers' },
  { to: '/rides', icon: MapPin, label: 'Ride Monitoring' },
  { to: '/revenue', icon: DollarSign, label: 'Revenue' },
  { to: '/notifications', icon: Bell, label: 'Notifications' },
  { to: '/complaints', icon: MessageSquareWarning, label: 'Complaints' },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      <div
        className={`sidebar-overlay ${isOpen ? 'visible' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="sidebar-logo">
              <Train size={22} />
            </div>
            <div>
              <span className="sidebar-brand-name">RailRide</span>
              <span className="sidebar-brand-tag">Admin Panel</span>
            </div>
          </div>
          <button className="sidebar-close" onClick={onClose} aria-label="Close menu">
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
              onClick={onClose}
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <p>© 2026 RailRide</p>
          <p className="sidebar-version">v1.0.0</p>
        </div>
      </aside>
    </>
  );
}
