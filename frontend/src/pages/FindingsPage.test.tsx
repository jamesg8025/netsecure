import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ScanFinding, ScanSummary } from '../api/client'
import FindingsPage from './FindingsPage'

function scan(overrides: Partial<ScanSummary>): ScanSummary {
  return {
    scan_id: 12,
    target: '192.168.1.0/24',
    profile: 'basic',
    timestamp: '2026-11-05T14:58:00Z',
    finished_at: '2026-11-05T15:00:00Z',
    status: 'Completed',
    error_message: null,
    devices_found: 2,
    findings_found: 3,
    ...overrides,
  }
}

// Most severe first, as the API returns them.
const findings: ScanFinding[] = [
  {
    finding_id: 1,
    severity: 'critical',
    finding: 'Telnet open',
    host: '192.168.1.8',
    port: 23,
    protocol: 'tcp',
    service: 'telnet',
    description: 'Telnet sends credentials in plain text.',
  },
  {
    finding_id: 2,
    severity: 'medium',
    finding: 'Unencrypted HTTP',
    host: '192.168.1.9',
    port: 80,
    protocol: 'tcp',
    service: 'http',
    description: 'Web traffic is not encrypted.',
  },
  {
    finding_id: 3,
    severity: 'info',
    finding: 'Untitled finding',
    host: '192.168.1.9',
    port: 445,
    protocol: 'tcp',
    service: null,
    description: 'SMB is reachable.',
  },
]

// Answers the scan list, and the findings request for any listed scan.
function mockApi(scans: ScanSummary[], scanFindings = findings) {
  const fetchMock = vi.fn<typeof fetch>(async (input) => {
    if (input === '/api/scans/') return Response.json({ scans })
    const scanId = Number(/^\/api\/scans\/(\d+)\/findings\/$/.exec(String(input))?.[1])
    if (scans.some((item) => item.scan_id === scanId)) {
      return Response.json({ scan_id: scanId, findings: scanFindings })
    }
    return new Response(null, { status: 404 })
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

// The page reads ?scan= from the URL, so it needs a router.
function renderPage(path = '/findings') {
  const router = createMemoryRouter(
    [
      { path: '/findings', element: <FindingsPage /> },
      { path: '/history', element: <h1>History</h1> },
    ],
    { initialEntries: [path] },
  )
  render(<RouterProvider router={router} />)
  return router
}

function cellsOf(row: HTMLElement) {
  return within(row).getAllByRole('cell').map((cell) => cell.textContent)
}

describe('FindingsPage (WBS 6.0/8.0)', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('loads findings for the newest completed scan from the API', async () => {
    const fetchMock = mockApi([scan({ scan_id: 13, status: 'Failed', error_message: 'Scan failed.' }), scan({})])
    renderPage()

    expect(screen.getByRole('status')).toHaveTextContent('Loading findings…')
    expect(await screen.findByText(/Showing scan #12 for 192\.168\.1\.0\/24/)).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/12/findings/', expect.anything())
    expect(screen.getByText('3 finding(s) found')).toBeInTheDocument()

    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(4)
    expect(cellsOf(rows[1])).toEqual([
      'Critical', 'Telnet open', '192.168.1.8', '23/tcp', 'telnet', 'Telnet sends credentials in plain text.',
    ])
    // A finding with no service name shows a dash in the Service column.
    expect(cellsOf(rows[3])).toEqual([
      'Info', 'Untitled finding', '192.168.1.9', '445/tcp', '—', 'SMB is reachable.',
    ])
  })

  it('filters by severity, including Info', async () => {
    const user = userEvent.setup()
    mockApi([scan({})])
    renderPage()
    await screen.findByText('3 finding(s) found')

    await user.selectOptions(screen.getByRole('combobox', { name: 'Severity' }), 'Info')
    expect(screen.getAllByRole('row')).toHaveLength(2)
    expect(cellsOf(screen.getAllByRole('row')[1])[1]).toBe('Untitled finding')

    await user.selectOptions(screen.getByRole('combobox', { name: 'Severity' }), 'High')
    expect(screen.getByText('No findings match your search.')).toBeInTheDocument()
  })

  it.each([' 445 ', '445/tcp', 'telnet plain'])('searches findings for %j', async (query) => {
    const user = userEvent.setup()
    mockApi([scan({})])
    renderPage()

    await user.type(await screen.findByPlaceholderText('Search findings...'), query)

    expect(screen.getAllByRole('row')).toHaveLength(2)
  })

  it("says an empty list doesn't mean the network is safe", async () => {
    mockApi([scan({ findings_found: 0 })], [])
    renderPage()

    expect(await screen.findByText(/No findings for this scan/)).toHaveTextContent(
      "doesn't mean the network is safe",
    )
    expect(screen.queryByPlaceholderText('Search findings...')).not.toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('shows the scan named by ?scan= instead of the newest one', async () => {
    const fetchMock = mockApi([scan({}), scan({ scan_id: 11, target: '10.0.0.0/24' })])
    renderPage('/findings?scan=11')

    expect(await screen.findByText(/Showing scan #11 for 10\.0\.0\.0\/24/)).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/11/findings/', expect.anything())
    expect(fetchMock).not.toHaveBeenCalledWith('/api/scans/12/findings/', expect.anything())
  })

  it('says when ?scan= names no saved scan', async () => {
    const fetchMock = mockApi([scan({})])
    renderPage('/findings?scan=99')

    expect(await screen.findByRole('alert')).toHaveTextContent('Scan #99 was not found.')
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('explains why a chosen failed scan has no findings', async () => {
    mockApi([scan({ scan_id: 13, status: 'Failed', error_message: 'Nmap exited with code 1.' })])
    renderPage('/findings?scan=13')

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Scan #13 of 192.168.1.0/24 failed: Nmap exited with code 1. It has no findings to show.',
    )
  })

  it('shows an error when the findings request fails', async () => {
    vi.stubGlobal('fetch', vi.fn<typeof fetch>(async (input) => (
      input === '/api/scans/'
        ? Response.json({ scans: [scan({})] })
        : new Response('Bad Gateway', { status: 502 })
    )))
    renderPage()

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Could not load findings. Check that the backend is running.',
    )
  })
})
