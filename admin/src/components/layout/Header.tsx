import { Menu, LogOut, User } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';

interface HeaderProps {
  title: string;
  onMenuClick: () => void;
}

export function Header({ title, onMenuClick }: HeaderProps) {
  const { admin, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <header className="header">
      <div className="header-left">
        <button className="header-menu-btn" onClick={onMenuClick} aria-label="Open menu">
          <Menu size={22} />
        </button>
        <h1 className="header-title">{title}</h1>
      </div>

      <div className="header-right">
        {admin && (
          <div className="header-user">
            <div className="header-avatar">
              <User size={16} />
            </div>
            <div className="header-user-info">
              <span className="header-user-name">{admin.full_name}</span>
              <span className="header-user-role">{admin.role}</span>
            </div>
          </div>
        )}
        <Button variant="ghost" size="sm" onClick={handleLogout} title="Logout">
          <LogOut size={18} />
        </Button>
      </div>
    </header>
  );
}
