import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ScanSummary } from '../api/client'
import HistoryPage from './HistoryPage'

const COMPLETED_AT = '2026-11-02T01:00:00Z'

function scan(overrides: Partial<ScanSummary>): ScanSummary {
  return {
    scan_id: 1,
    target: '192.168.1.1',
    profile: 'basic',
    timestamp: COMPLETED_AT,
    finished_at: '2026-11-02T01:01:00Z',
    status: 'Completed',
    error_message: null,
    devices_found: 2,
    findings_found: 1,
    ...overrides,
  }
}

function mockScans(scans: ScanSummary[]) {
  const fetchMock = vi.fn<typeof fetch>(async () => Response.json({ scans }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

// The page links to Devices, so it needs a router.
function renderPage() {
  const router = createMemoryRouter(
    [
      { path: '/history', element: <HistoryPage /> },
      { path: '/devices', element: <h1>Devices</h1> },
      { path: '/findings', element: <h1>Findings</h1> },
    ],
    { initialEntries: ['/history'] },
  )
  return { router, ...render(<RouterProvider router={router} />) }
}

// The table's body rows, without the header row.
function rows() {
  return screen.getAllByRole('row').slice(1)
}

describe('HistoryPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shows a loading state, then the saved scans in API order', async () => {
    const fetchMock = mockScans([
      scan({ scan_id: 2, target: '10.0.0.5', devices_found: 7, findings_found: 3 }),
      scan({ scan_id: 1, target: '192.168.1.1' }),
    ])

    renderPage()

    expect(screen.getByRole('status')).toHaveTextContent('Loading scans…')
    expect(await screen.findByText('2 scan(s) found.')).toBeInTheDocument()
    expect(screen.queryByText('Loading scans…')).not.toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/scans/', expect.anything())

    const [newest, oldest] = rows()
    const cells = within(newest).getAllByRole('cell').map((cell) => cell.textContent)
    expect(cells).toEqual(['10.0.0.5', new Date(COMPLETED_AT).toLocaleString(), 'Completed', '7', '3', 'View devicesView findings'])
    expect(oldest).toHaveTextContent('192.168.1.1')
  })

  it('tells "no scans yet" apart from "no scans match"', async () => {
    mockScans([])
    renderPage()

    expect(await screen.findByText(/No scans yet/)).toBeInTheDocument()
    expect(screen.queryByText(/No scans match/)).not.toBeInTheDocument()
    expect(screen.queryByText(/scan\(s\) found/)).not.toBeInTheDocument()
  })

  it('shows "no scans match" when the search excludes every scan', async () => {
    const user = userEvent.setup()
    mockScans([scan({})])
    renderPage()
    await screen.findByText('1 scan(s) found.')

    await user.type(screen.getByPlaceholderText('Search scans...'), 'nothing-like-this')

    expect(screen.getByText('No scans match your search.')).toBeInTheDocument()
    expect(screen.queryByText(/No scans yet/)).not.toBeInTheDocument()
  })

  it('searches by target', async () => {
    const user = userEvent.setup()
    mockScans([scan({ scan_id: 2, target: '10.0.0.5' }), scan({ scan_id: 1, target: '192.168.1.1' })])
    renderPage()
    await screen.findByText('2 scan(s) found.')

    await user.type(screen.getByPlaceholderText('Search scans...'), '10.0')

    expect(rows()).toHaveLength(1)
    expect(rows()[0]).toHaveTextContent('10.0.0.5')
  })

  it('filters by status', async () => {
    const user = userEvent.setup()
    mockScans([
      scan({ scan_id: 2, target: '10.0.0.5', status: 'Failed', error_message: 'Nmap failed.' }),
      scan({ scan_id: 1, target: '192.168.1.1' }),
    ])
    renderPage()
    await screen.findByText('2 scan(s) found.')

    await user.selectOptions(screen.getByRole('combobox'), 'Failed')

    expect(rows()).toHaveLength(1)
    expect(rows()[0]).toHaveTextContent('10.0.0.5')
  })

  it('filters to pending scans', async () => {
    const user = userEvent.setup()
    mockScans([
      scan({ scan_id: 2, target: '10.0.0.5', timestamp: null, finished_at: null, status: 'Pending' }),
      scan({ scan_id: 1, target: '192.168.1.1' }),
    ])
    renderPage()
    await screen.findByText('2 scan(s) found.')

    await user.selectOptions(screen.getByRole('combobox'), 'Pending')

    expect(rows()).toHaveLength(1)
    expect(rows()[0]).toHaveTextContent('10.0.0.5')
  })

  it('shows why a scan failed (NFR-04)', async () => {
    mockScans([
      scan({ scan_id: 2, target: '10.0.0.5', status: 'Failed', error_message: 'Nmap could not be run.' }),
      scan({ scan_id: 1, target: '192.168.1.1' }),
    ])
    renderPage()
    await screen.findByText('2 scan(s) found.')

    const [failed, completed] = rows()
    expect(failed).toHaveTextContent('Nmap could not be run.')
    expect(completed).not.toHaveTextContent('Nmap could not be run.')
  })

  it('shows "Not started" for a null timestamp, in the table and the search', async () => {
    const user = userEvent.setup()
    mockScans([
      scan({ scan_id: 2, target: '10.0.0.5', timestamp: null, finished_at: null, status: 'Pending' }),
      scan({ scan_id: 1, target: '192.168.1.1' }),
    ])
    renderPage()
    await screen.findByText('2 scan(s) found.')

    expect(rows()[0]).toHaveTextContent('Not started')
    expect(rows()[0]).not.toHaveTextContent('1970')

    await user.type(screen.getByPlaceholderText('Search scans...'), 'not started')

    expect(rows()).toHaveLength(1)
    expect(rows()[0]).toHaveTextContent('10.0.0.5')
  })

  it("shows the backend's error message", async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Response.json(
      { error: { code: 'internal_error', message: 'Something went wrong on the server.' } },
      { status: 500 },
    )))

    renderPage()

    expect(await screen.findByRole('alert')).toHaveTextContent('Something went wrong on the server.')
    expect(screen.queryByText(/No scans yet/)).not.toBeInTheDocument()
  })

  it.each([
    ['the proxy returns a non-JSON error', async () => new Response('Bad Gateway', { status: 502 })],
    ['the request fails', async () => { throw new TypeError('Failed to fetch') }],
  ])('shows a friendly message when %s', async (_name, impl) => {
    vi.stubGlobal('fetch', vi.fn(impl))

    renderPage()

    expect(await screen.findByRole('alert')).toHaveTextContent('Could not load scan history.')
  })

  it("opens a completed scan's devices, and offers no link for other scans (UC-05)", async () => {
    const user = userEvent.setup()
    mockScans([
      scan({ scan_id: 3, target: '10.0.0.7', status: 'Failed', error_message: 'Nmap failed.' }),
      scan({ scan_id: 2, target: '10.0.0.5' }),
    ])
    const { router } = renderPage()
    await screen.findByText('2 scan(s) found.')

    const [failed, completed] = rows()
    expect(within(failed).queryByRole('link')).not.toBeInTheDocument()
    await user.click(within(completed).getByRole('link', { name: 'View devices for scan #2' }))

    expect(router.state.location.pathname).toBe('/devices')
    expect(router.state.location.search).toBe('?scan=2')
  })

  it("opens a completed scan's findings", async () => {
    const user = userEvent.setup()
    mockScans([scan({ scan_id: 2, target: '10.0.0.5' })])
    const { router } = renderPage()
    await screen.findByText('1 scan(s) found.')

    await user.click(screen.getByRole('link', { name: 'View findings for scan #2' }))

    expect(router.state.location.pathname).toBe('/findings')
    expect(router.state.location.search).toBe('?scan=2')
  })

  it('cancels the request when the page unmounts', () => {
    const fetchMock = mockScans([])

    const { unmount } = renderPage()
    const signal = fetchMock.mock.calls[0][1]!.signal!
    expect(signal.aborted).toBe(false)

    unmount()

    expect(signal.aborted).toBe(true)
  })
})
