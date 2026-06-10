import { useState, type FormEvent } from 'react';
import { Navigate } from 'react-router-dom';
import { Mail, Lock, Train } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { ApiClientError } from '@/services/api';

export function LoginPage() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (isLoading) {
    return (
      <div className="login-page">
        <div className="login-loading">Loading...</div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await login({ email, password });
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.detail : 'Login failed. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-brand">
          <div className="login-logo">
            <Train size={32} />
          </div>
          <h1>RailRide</h1>
          <p>Admin Dashboard</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <h2>Sign in to your account</h2>
          <p className="login-subtitle">Enter your credentials to access the admin panel</p>

          {error && <div className="alert alert-error">{error}</div>}

          <Input
            label="Email address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@railride.com"
            leftIcon={<Mail size={18} />}
            required
            autoComplete="email"
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            leftIcon={<Lock size={18} />}
            required
            autoComplete="current-password"
          />

          <Button type="submit" loading={submitting} className="login-submit">
            Sign in
          </Button>
        </form>

        <p className="login-footer">
          Protected area. Authorized personnel only.
        </p>
      </div>
    </div>
  );
}
