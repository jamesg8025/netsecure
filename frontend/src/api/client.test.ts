import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  ApiError,
  apiGet,
  apiPost,
  listScanDevices,
  listScanFindings,
  listScans,
  login,
  type ScanDevice,
  type ScanFinding,
  type ScanSummary,
} from './client'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('apiGet', () => {
  it("uses the backend's error message and code", async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Response.json(
      { error: { code: 'internal_error', message: 'Something went wrong.' } },
      { status: 500 },
    )))

    const error = await apiGet('/scans/').catch((err: unknown) => err)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 500, code: 'internal_error', message: 'Something went wrong.' })
  })

  it('falls back to a generic message when the body is not JSON', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('Bad Gateway', { status: 502 })))

    const error = await apiGet('/scans/').catch((err: unknown) => err)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 502, code: undefined, message: 'GET /api/scans/ failed with 502' })
  })
})

describe('login', () => {
  it('posts credentials and uses the rotated CSRF token on the next POST', async () => {
    const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
      if (input === '/api/csrf/') return Response.json({ csrfToken: 'csrf-before-login' })
      if (input === '/api/auth/login/') {
        expect(JSON.parse(String(init?.body))).toEqual({ username: 'izaiah', password: ' p a s s ' })
        expect((init?.headers as Record<string, string>)['X-CSRFToken']).toBe('csrf-before-login')
        return Response.json({
          user: { id: 4, username: 'izaiah' },
          csrfToken: 'csrf-after-login',
        })
      }
      if (input === '/api/scans/') return Response.json({ ok: true })
      return new Response(null, { status: 404 })
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(login('izaiah', ' p a s s ')).resolves.toEqual({
      user: { id: 4, username: 'izaiah' },
      csrfToken: 'csrf-after-login',
    })
    await apiPost('/scans/', {})

    const nextPost = fetchMock.mock.calls.find(([url]) => url === '/api/scans/')
    expect((nextPost?.[1]?.headers as Record<string, string>)['X-CSRFToken']).toBe('csrf-after-login')
  })
})

describe('listScans', () => {
  it('requests the scan list and returns its rows', async () => {
    const scans: ScanSummary[] = [{
      scan_id: 1,
      target: '127.0.0.1',
      profile: 'basic',
      timestamp: '2026-11-02T01:00:00Z',
      finished_at: '2026-11-02T01:01:00Z',
      status: 'Completed',
      error_message: null,
      devices_found: 1,
      findings_found: 0,
    }]
    const fetchMock = vi.fn(async () => Response.json({ scans }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(listScans()).resolves.toEqual(scans)
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/', expect.anything())
  })
})

describe('listScanDevices', () => {
  it('requests device rows for the selected scan and returns them', async () => {
    const devices: ScanDevice[] = [{
      host_id: 7,
      ip_address: '192.168.1.8',
      hostname: 'nas.local',
      service_id: 3,
      port: 443,
      protocol: 'tcp',
      service: 'https',
      product: 'nginx',
      version: '1.24.0',
    }]
    const fetchMock = vi.fn(async () => Response.json({ scan_id: 12, devices }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(listScanDevices(12)).resolves.toEqual(devices)
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/12/devices/', expect.anything())
  })
})

describe('listScanFindings', () => {
  it('requests findings for the selected scan and returns them', async () => {
    const findings: ScanFinding[] = [{
      finding_id: 1,
      severity: 'critical',
      finding: 'Telnet open',
      host: '192.168.1.8',
      port: 23,
      protocol: 'tcp',
      service: 'telnet',
      description: 'Telnet sends credentials in plain text.',
    }]
    const fetchMock = vi.fn(async () => Response.json({ scan_id: 12, findings }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(listScanFindings(12)).resolves.toEqual(findings)
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/12/findings/', expect.anything())
  })
})
