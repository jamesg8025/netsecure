import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import NewScanPage from './NewScanPage'

type ScanReply = { status: number; body: unknown }

// Answers the CSRF request and replies to POST /api/scans/ with `scan`.
function mockBackend(scan: ScanReply | Promise<ScanReply>) {
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    if (url === '/api/csrf/') return Response.json({ csrfToken: 'token-123' })
    if (url === '/api/scans/' && init?.method === 'POST') {
      const { status, body } = await scan
      return Response.json(body, { status })
    }
    return new Response(null, { status: 404 })
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

async function submit(target: string) {
  const user = userEvent.setup()
  render(<NewScanPage />)
  await user.type(screen.getByLabelText(/Target/), target)
  await user.click(screen.getByRole('button', { name: 'Start Scan' }))
}

describe('NewScanPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('uses a pointer cursor and enabled hover styling for the scan button', () => {
    render(<NewScanPage />)

    expect(screen.getByRole('button', { name: 'Start Scan' })).toHaveClass(
      'cursor-pointer',
      'enabled:hover:bg-slate-800',
    )
  })

  it('posts the target with a CSRF token and lists the results', async () => {
    const fetchMock = mockBackend({
      status: 200,
      body: {
        target: '192.168.1.1',
        profile: 'basic',
        hosts: [{
          ip: '192.168.1.1',
          hostname: 'router',
          services: [{ port: 80, protocol: 'tcp', service: 'http', product: 'nginx', version: '1.25' }],
        }],
      },
    })

    await submit('192.168.1.1')

    expect(await screen.findByText(/1 active host found/)).toBeInTheDocument()
    const results = screen.getByRole('list', { name: 'Scan results' })
    expect(results).toHaveTextContent('192.168.1.1 (router)')
    expect(results).toHaveTextContent('80/tcp http — nginx 1.25')

    const [, init] = fetchMock.mock.calls.find(([url]) => url === '/api/scans/')!
    expect(JSON.parse(init!.body as string)).toEqual({ target: '192.168.1.1', profile: 'basic' })
    expect((init!.headers as Record<string, string>)['X-CSRFToken']).toBe('token-123')
  })

  it('shows a scanning state until the scan finishes', async () => {
    let finish!: (reply: ScanReply) => void
    mockBackend(new Promise((resolve) => { finish = resolve }))

    await submit('192.168.1.1')

    const button = await screen.findByRole('button', { name: 'Scanning…' })
    expect(button).toBeDisabled()
    expect(within(button).getByTestId('spinner')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Scanning 192.168.1.1… This can take a few minutes.')
    expect(screen.getByTestId('scan-progress-bar')).toHaveAttribute('aria-hidden', 'true')

    finish({ status: 200, body: { target: '192.168.1.1', profile: 'basic', hosts: [] } })

    expect(await screen.findByText(/0 active hosts found/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Start Scan' })).toBeEnabled()
    expect(screen.queryByTestId('spinner')).not.toBeInTheDocument()
    expect(screen.queryByTestId('scan-progress')).not.toBeInTheDocument()
  })

  describe('elapsed timer', () => {
    beforeEach(() => {
      vi.useFakeTimers({ shouldAdvanceTime: true })
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('counts up while scanning, outside the status region, and resets for the next scan', async () => {
      let finish!: (reply: ScanReply) => void
      const fetchMock = mockBackend(new Promise((resolve) => { finish = resolve }))
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
      render(<NewScanPage />)
      await user.type(screen.getByLabelText(/Target/), '192.168.1.1')
      await user.click(screen.getByRole('button', { name: 'Start Scan' }))

      const elapsed = await screen.findByTestId('scan-elapsed')
      expect(elapsed).toHaveTextContent('Elapsed time 0:00')
      expect(screen.getByRole('status')).not.toContainElement(elapsed)

      act(() => { vi.advanceTimersByTime(5000) })
      expect(elapsed).toHaveTextContent('0:05')

      act(() => { vi.advanceTimersByTime(60_000) })
      expect(elapsed).toHaveTextContent('1:05')

      finish({ status: 200, body: { target: '192.168.1.1', profile: 'basic', hosts: [] } })
      expect(await screen.findByText(/0 active hosts found/)).toBeInTheDocument()
      expect(screen.queryByTestId('scan-elapsed')).not.toBeInTheDocument()

      // A second scan starts the timer from zero again.
      fetchMock.mockImplementation(async (url: string) => {
        if (url === '/api/csrf/') return Response.json({ csrfToken: 'token-123' })
        return new Promise<Response>(() => {})
      })
      await user.click(screen.getByRole('button', { name: 'Start Scan' }))
      expect(await screen.findByTestId('scan-elapsed')).toHaveTextContent('0:00')
    })
  })

  it('removes the progress indicator when the scan fails', async () => {
    mockBackend({
      status: 500,
      body: { error: { code: 'scan_failed', message: 'Nmap is not installed.' } },
    })

    await submit('192.168.1.1')

    expect(await screen.findByRole('alert')).toHaveTextContent('Nmap is not installed.')
    expect(screen.queryByTestId('scan-progress')).not.toBeInTheDocument()
    expect(screen.queryByTestId('spinner')).not.toBeInTheDocument()
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it("shows the backend's error message when the target is rejected", async () => {
    mockBackend({
      status: 400,
      body: { error: { code: 'invalid_target', message: 'NetSecure only allows authorized private network targets.' } },
    })

    await submit('8.8.8.8')

    expect(await screen.findByRole('alert')).toHaveTextContent('NetSecure only allows authorized private network targets.')
    expect(screen.queryByRole('list', { name: 'Scan results' })).not.toBeInTheDocument()
  })
})
