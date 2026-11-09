import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { routes } from './routes'
import { AuthProvider } from './auth/AuthContext'
import { clearCsrfToken } from './api/client'

function renderAt(path: string, fetchMock?: typeof fetch) {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  if (fetchMock) vi.stubGlobal('fetch', fetchMock)
  render(<AuthProvider><RouterProvider router={router} /></AuthProvider>)
  return router
}

describe('dashboard routes', () => {
  // The layout's BackendStatus calls the health endpoint on mount, and the
  // History page loads the scan list.
  beforeEach(() => {
    clearCsrfToken()
    vi.stubGlobal('fetch', vi.fn(async (url: string) => {
      if (url === '/api/auth/me/') return Response.json({ user: { id: 4, username: 'izaiah' } })
      if (url === '/api/scans/') return Response.json({ scans: [] })
      return Response.json({ status: 'ok' })
    }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    clearCsrfToken()
  })

  it('redirects the root path to New Scan', async () => {
    const router = renderAt('/')

    expect(await screen.findByRole('heading', { name: 'New Scan' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/scan')
  })

  it('shows a nav link for every page', async () => {
    renderAt('/scan')

    await screen.findByRole('heading', { name: 'New Scan' })
    const nav = screen.getByRole('navigation', { name: 'Main' })
    for (const label of ['New Scan', 'Devices', 'Findings', 'History']) {
      expect(nav).toContainElement(screen.getByRole('link', { name: label }))
    }
  })

  it('renders the login page outside the dashboard layout', async () => {
    const fetchMock = vi.fn<typeof fetch>(async (url) => (
      url === '/api/auth/me/'
        ? Response.json({ error: { code: 'not_authenticated' } }, { status: 401 })
        : Response.json({ status: 'ok' })
    ))
    renderAt('/login', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
    expect(screen.queryByRole('navigation', { name: 'Main' })).not.toBeInTheDocument()
  })

  it('redirects an already logged-in user away from the login page', async () => {
    const router = renderAt('/login')

    expect(await screen.findByRole('heading', { name: 'New Scan' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/scan')
  })

  it('navigates between pages and marks the current link', async () => {
    const user = userEvent.setup()
    renderAt('/scan')
    await screen.findByRole('heading', { name: 'New Scan' })

    await user.click(screen.getByRole('link', { name: 'Findings' }))

    expect(screen.getByRole('heading', { name: 'Findings' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Findings' })).toHaveAttribute('aria-current', 'page')
    expect(screen.getByRole('link', { name: 'New Scan' })).not.toHaveAttribute('aria-current')
  })

  it.each([
    ['/devices', 'Devices'],
    ['/history', 'History'],
  ])('renders %s directly', async (path, heading) => {
    renderAt(path)

    expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
  })

  it('shows a not-found page for unknown paths', async () => {
    renderAt('/nope')

    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Go to New Scan' })).toHaveAttribute('href', '/scan')
  })

  it('toggles the mobile menu', async () => {
    const user = userEvent.setup()
    renderAt('/scan')
    await screen.findByRole('heading', { name: 'New Scan' })
    const button = screen.getByRole('button', { name: 'Menu' })

    expect(button).toHaveAttribute('aria-expanded', 'false')
    await user.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')
    await user.click(screen.getByRole('link', { name: 'Devices' }))
    expect(button).toHaveAttribute('aria-expanded', 'false')
  })

  it('redirects a logged-out user back to the requested page after login', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      if (input === '/api/auth/me/') return Response.json({ error: { code: 'not_authenticated' } }, { status: 401 })
      if (input === '/api/csrf/') return Response.json({ csrfToken: 'csrf-before-login' })
      if (input === '/api/auth/login/') return Response.json({ user: { id: 4, username: 'izaiah' }, csrfToken: 'csrf-after-login' })
      if (input === '/api/health/') return Response.json({ status: 'ok' })
      if (input === '/api/scans/7/devices/') return Response.json({ scan_id: 7, devices: [] })
      return new Response(null, { status: 404 })
    })
    const router = renderAt('/devices?scan=7', fetchMock)

    await user.type(await screen.findByLabelText('Username'), 'izaiah')
    await user.type(screen.getByLabelText('Password'), 'secret')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('heading', { name: 'Devices' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/devices')
    expect(router.state.location.search).toBe('?scan=7')
  })

  it('shows the authenticated username and logs out with a fresh CSRF token on the next login', async () => {
    const user = userEvent.setup()
    let csrfRequests = 0
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      if (input === '/api/auth/me/') return Response.json({ user: { id: 4, username: 'izaiah' } })
      if (input === '/api/health/') return Response.json({ status: 'ok' })
      if (input === '/api/csrf/') return Response.json({ csrfToken: `csrf-${++csrfRequests}` })
      if (input === '/api/auth/logout/') return new Response(null, { status: 204 })
      if (input === '/api/auth/login/') return Response.json({ user: { id: 4, username: 'izaiah' }, csrfToken: 'csrf-after-login' })
      return new Response(null, { status: 404 })
    })
    renderAt('/scan', fetchMock)

    expect(await screen.findByText('izaiah')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Log out' }))
    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/auth/logout/', expect.objectContaining({ method: 'POST' }))

    await user.type(screen.getByLabelText('Username'), 'izaiah')
    await user.type(screen.getByLabelText('Password'), 'secret')
    await user.click(screen.getByRole('button', { name: 'Log in' }))
    expect(await screen.findByRole('heading', { name: 'New Scan' })).toBeInTheDocument()
    expect(csrfRequests).toBe(2)
  })

  it('redirects to login when a dashboard data request returns 401', async () => {
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      if (input === '/api/auth/me/') return Response.json({ user: { id: 4, username: 'izaiah' } })
      if (input === '/api/scans/') return Response.json({ error: { code: 'not_authenticated' } }, { status: 401 })
      return Response.json({ status: 'ok' })
    })
    const router = renderAt('/history', fetchMock)

    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/login')
    expect((router.state.location.state as { from: { pathname: string } }).from.pathname).toBe('/history')
  })

  it('does not render the dashboard while the session check is pending', async () => {
    let resolveMe!: (response: Response) => void
    const fetchMock = vi.fn<typeof fetch>(async (input) => {
      if (input === '/api/auth/me/') return new Promise<Response>((resolve) => { resolveMe = resolve })
      return Response.json({ status: 'ok' })
    })
    renderAt('/history', fetchMock)

    expect(screen.getByRole('status')).toHaveTextContent('Checking your session')
    expect(screen.queryByRole('navigation', { name: 'Main' })).not.toBeInTheDocument()

    resolveMe(Response.json({ error: { code: 'not_authenticated' } }, { status: 401 }))
    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
    expect(screen.queryByRole('navigation', { name: 'Main' })).not.toBeInTheDocument()
  })
})
