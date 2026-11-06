// Thin wrapper around fetch for the Django API. In development, Vite proxies
// /api to the backend (see vite.config.ts), so paths stay relative.

export class ApiError extends Error {
  readonly status: number
  readonly code?: string

  constructor(status: number, message: string, code?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

type ErrorBody = { error?: { code?: string; message?: string } }

// Turn a failed response into an ApiError, using the backend's
// {"error": {"code", "message"}} body when it has one.
async function toApiError(response: Response, fallback: string): Promise<ApiError> {
  try {
    const body = (await response.json()) as ErrorBody
    if (body.error?.message) {
      return new ApiError(response.status, body.error.message, body.error.code)
    }
  } catch {
    // Not JSON (e.g. the proxy could not reach Django); use the fallback.
  }
  return new ApiError(response.status, fallback)
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: { Accept: 'application/json' },
    signal,
  })
  if (!response.ok) {
    throw await toApiError(response, `GET /api${path} failed with ${response.status}`)
  }
  return (await response.json()) as T
}

let csrfToken: string | undefined

async function getCsrfToken(): Promise<string> {
  csrfToken ??= (await apiGet<{ csrfToken: string }>('/csrf/')).csrfToken
  return csrfToken
}

export async function apiPost<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': await getCsrfToken(),
    },
    body: JSON.stringify(body),
    signal,
  })
  if (!response.ok) {
    if (response.status === 403) csrfToken = undefined
    throw await toApiError(response, `POST /api${path} failed with ${response.status}`)
  }
  return (await response.json()) as T
}

export type HealthResponse = { status: 'ok' }

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiGet<HealthResponse>('/health/', signal)
}

// Matches the scanner's result contract (docs/SCANNER_HANDOFF.md).
export type ScanService = {
  port: number
  protocol: string
  service: string
  product: string
  version: string
}

export type ScanHost = {
  ip: string
  hostname: string
  services: ScanService[]
}

export type ScanProfile = 'basic' | 'discovery'

export type ScanResponse = {
  target: string
  profile: ScanProfile
  hosts: ScanHost[]
}

export function startScan(target: string, profile: ScanProfile = 'basic'): Promise<ScanResponse> {
  return apiPost<ScanResponse>('/scans/', { target, profile })
}

export type ScanStatus = 'Pending' | 'In-Progress' | 'Completed' | 'Failed'

// One row of GET /api/scans/ (docs/ARCHITECTURE.md, API Endpoints).
export type ScanSummary = {
  scan_id: number
  target: string
  profile: ScanProfile
  // ISO 8601 UTC start time; null for a scan that never started.
  timestamp: string | null
  finished_at: string | null
  status: ScanStatus
  // Set only for failed scans.
  error_message: string | null
  devices_found: number
  findings_found: number
}

// Saved scans, newest first.
export async function listScans(signal?: AbortSignal): Promise<ScanSummary[]> {
  const { scans } = await apiGet<{ scans: ScanSummary[] }>('/scans/', signal)
  return scans
}
