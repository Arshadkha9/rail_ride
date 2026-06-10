interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeMap = {
  sm: 20,
  md: 32,
  lg: 48,
};

export function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  const dimension = sizeMap[size];
  return (
    <div className={`spinner-container ${className}`} role="status" aria-label="Loading">
      <svg
        className="spinner"
        width={dimension}
        height={dimension}
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          className="spinner-track"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="3"
        />
        <path
          className="spinner-head"
          d="M12 2a10 10 0 0 1 10 10"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

export function PageLoader() {
  return (
    <div className="page-loader">
      <Spinner size="lg" />
      <p>Loading...</p>
    </div>
  );
}
