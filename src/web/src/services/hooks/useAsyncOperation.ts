import { useState, useCallback } from "react";

export interface AsyncOperationState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  loadingMessage: string;
}

export interface AsyncOperationActions<T> {
  execute: (...args: any[]) => Promise<T | undefined>;
  reset: () => void;
}

export interface AsyncServiceMethod<T> {
  loadingMessage: string;
  fn: (...args: any[]) => Promise<T>;
}

export interface UseAsyncOperationResult<T> extends AsyncOperationState<T>, AsyncOperationActions<T> {}

/**
 * Generic hook for wrapping async service operations with loading states and messages.
 *
 * @param serviceMethod - Object containing the async function and loading message
 * @returns Object with data, loading, error, loadingMessage, execute, and reset
 *
 * @example
 * ```typescript
 * const resourceProviders = useAsyncOperation({
 *   loadingMessage: "Loading resource providers...",
 *   fn: specsApi.getResourceProviders
 * });
 *
 * // Usage
 * await resourceProviders.execute(moduleUrl);
 *
 * // In JSX
 * {resourceProviders.loading && (
 *   <Box>
 *     <CircularProgress />
 *     <Typography>{resourceProviders.loadingMessage}</Typography>
 *   </Box>
 * )}
 * ```
 */
export const useAsyncOperation = <T>(serviceMethod?: AsyncServiceMethod<T>): UseAsyncOperationResult<T> => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [loadingMessage, setLoadingMessage] = useState<string>("");

  const execute = useCallback(
    async (...args: any[]): Promise<T | undefined> => {
      if (!serviceMethod) {
        console.warn("useAsyncOperation: No service method provided");
        return;
      }

      setLoading(true);
      setError(null);
      setLoadingMessage(serviceMethod.loadingMessage);

      try {
        const result = await serviceMethod.fn(...args);
        setData(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setLoading(false);
        setLoadingMessage("");
      }
    },
    [serviceMethod],
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    setLoadingMessage("");
  }, []);

  return {
    data,
    loading,
    error,
    loadingMessage,
    execute,
    reset,
  };
};
