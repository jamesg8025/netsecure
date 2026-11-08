import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ScanDevice, ScanSummary } from '../api/client'
import DevicesPage from './DevicesPage'

const COMPLETED_AT = '2026-11-05T15:00:00Z'

function scan(overrides: Partial<ScanSummary>): ScanSummary {
  return {
    scan_id: 12,
    target: '192.168.1.0/24',
    profile: 'basic',
    timestamp: '2026-11-05T14:58:00Z',
    finished_at: COMPLETED_AT,
    status: 'Completed',
    error_message: null,
    devices_found: 1,
    findings_found: 0,
    ...overrides,
  }
}

const devices: ScanDevice[] = [
  {
    host_id: 7,
    ip_address: '192.168.1.8',
    hostname: 'nas.local',
    service_id: 3,
    port: 443,
    protocol: 'tcp',
    service: 'https',
    product: 'nginx',
    version: '1.24.0',
  },
  {
    host_id: 7,
    ip_address: '192.168.1.8',
    hostname: 'nas.local',
    service_id: 4,
    port: 22,
    protocol: 'tcp',
    service: 'ssh',
    product: 'OpenSSH',
    version: '9.6p1',
  },
  {
    host_id: 8,
    ip_address: '192.168.1.9',
    hostname: null,
    service_id: null,
    port: null,
    protocol: null,
    service: null,
    product: null,
    version: null,
  },
]

function mockApi(scans: ScanSummary[], scanDevices = devices) {
  const fetchMock = vi.fn<typeof fetch>(async (input) => {
    if (input === '/api/scans/') return Response.json({ scans })
    if (input === '/api/scans/12/devices/') {
      return Response.json({ scan_id: 12, devices: scanDevices })
    }
    return new Response(null, { status: 404 })
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('DevicesPage (WBS 6.0/8.0)', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('loads devices for the newest completed scan from the API', async () => {
    const fetchMock = mockApi([
      scan({ scan_id: 13, status: 'Failed', error_message: 'Scan failed.' }),
      scan({}),
    ])
    render(<DevicesPage />)

    expect(screen.getByRole('status')).toHaveTextContent('Loading devices…')
    expect(await screen.findByText(/Showing scan #12 for 192\.168\.1\.0\/24/)).toBeInTheDocument()
    expect(screen.getByText('2 devices found · 3 rows shown')).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/12/devices/', expect.anything())

    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(4)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.8', 'nas.local', '443/tcp', 'https', 'nginx', '1.24.0',
    ])
    expect(within(rows[3]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.9', '—', '—', '—', '—', '—',
    ])
  })

  it('shows TCP and UDP separately when a host uses the same port number', async () => {
    const tcp = { ...devices[0], service_id: 10, port: 5353, protocol: 'tcp', service: 'mdns-tcp' }
    const udp = { ...devices[0], service_id: 11, port: 5353, protocol: 'udp', service: 'mdns-udp' }
    mockApi([scan({})], [tcp, udp])
    render(<DevicesPage />)

    expect(await screen.findByText('1 device found · 2 rows shown')).toBeInTheDocument()
    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(3)
    expect(within(rows[1]).getAllByRole('cell')[2]).toHaveTextContent('5353/tcp')
    expect(within(rows[2]).getAllByRole('cell')[2]).toHaveTextContent('5353/udp')
  })

  it('searches across combined host and service fields, as well as product and version', async () => {
    const user = userEvent.setup()
    mockApi([scan({})])
    render(<DevicesPage />)

    const search = await screen.findByPlaceholderText(/search by ip, hostname, service, product, or version/i)
    await user.type(search, 'nas.local ssh')

    let rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(2)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.8', 'nas.local', '22/tcp', 'ssh', 'OpenSSH', '9.6p1',
    ])

    await user.clear(search)
    await user.type(search, 'openssh')

    rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(2)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.8', 'nas.local', '22/tcp', 'ssh', 'OpenSSH', '9.6p1',
    ])

    await user.clear(search)
    await user.type(search, '1.24.0')

    rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(2)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.8', 'nas.local', '443/tcp', 'https', 'nginx', '1.24.0',
    ])
  })

  it('shows a helpful empty state when no completed scan exists', async () => {
    const fetchMock = mockApi([
      scan({ scan_id: 13, status: 'Failed', error_message: 'Scan failed.' }),
      scan({ scan_id: 12, status: 'In-Progress', finished_at: null }),
    ])
    render(<DevicesPage />)

    expect(await screen.findByText(/No completed scans yet/)).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('shows a helpful empty state when a completed scan found no devices', async () => {
    mockApi([scan({ devices_found: 0 })], [])
    render(<DevicesPage />)

    expect(await screen.findByText(/No devices were found in this scan/)).toBeInTheDocument()
  })

  it('shows a separate message when the search has no matches', async () => {
    const user = userEvent.setup()
    mockApi([scan({})])
    render(<DevicesPage />)

    await user.type(await screen.findByPlaceholderText(/search by ip/i), 'no-such-device')
    expect(screen.getByText(/No devices match your search/)).toBeInTheDocument()
    expect(screen.queryByText(/No devices were found in this scan/)).not.toBeInTheDocument()
  })

  it('shows a backend scan_not_found response as an error', async () => {
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      if (input === '/api/scans/') return Response.json({ scans: [scan({})] })
      return Response.json(
        { error: { code: 'scan_not_found', message: 'Scan not found.' } },
        { status: 404 },
      )
    })
    vi.stubGlobal('fetch', fetchMock)
    render(<DevicesPage />)

    expect(await screen.findByRole('alert')).toHaveTextContent('Scan not found.')
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/12/devices/', expect.anything())
  })

  it('shows an error when the scan history request fails', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('Unavailable', { status: 503 })))
    render(<DevicesPage />)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Could not load devices. Check that the backend is running.',
    )
  })
})
