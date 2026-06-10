import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiClientError } from '@/services/api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  refetch: () => Promise<void>;
  setData: React.Dispatch<React.SetStateAction<T | null>>;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
  enabled = true
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: enabled,
    error: null,
  });

  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const refetch = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fetcherRef.current();
      setState({ data, loading: false, error: null });
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.detail : 'An unexpected error occurred';
      setState({ data: null, loading: false, error: message });
    }
  }, []);

  useEffect(() => {
    if (enabled) {
      refetch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, refetch, ...deps]);

  return {
    ...state,
    refetch,
    setData: (value) =>
      setState((prev) => ({
        ...prev,
        data: typeof value === 'function' ? (value as (d: T | null) => T | null)(prev.data) : value,
      })),
  };
}

export function useMutation<TArgs extends unknown[], TResult>(
  mutator: (...args: TArgs) => Promise<TResult>
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(
    async (...args: TArgs): Promise<TResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const result = await mutator(...args);
        setLoading(false);
        return result;
      } catch (err) {
        const message =
          err instanceof ApiClientError ? err.detail : 'An unexpected error occurred';
        setError(message);
        setLoading(false);
        return null;
      }
    },
    [mutator]
  );

  return { mutate, loading, error, setError };
}
