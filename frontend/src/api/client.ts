// Thin wrapper around fetch for the Django API. In development, Vite proxies
// /api to the backend (see vite.config.ts), so paths stay relative.

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: { Accept: 'application/json' },
    signal,
  })
  if (!response.ok) {
    throw new ApiError(response.status, `GET /api${path} failed with ${response.status}`)
  }
  return (await response.json()) as T
}

export type HealthResponse = { status: 'ok' }

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiGet<HealthResponse>('/health/', signal)
}
