export function createApiState({ data = null, isLoading = false, error = null } = {}) {
  return {
    data,
    isLoading,
    error,
    isEmpty: Array.isArray(data) ? data.length === 0 : !data,
  };
}
