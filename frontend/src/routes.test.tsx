import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { routes } from './routes'

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  render(<RouterProvider router={router} />)
  return router
}

describe('dashboard routes', () => {
  // The layout's BackendStatus calls the health endpoint on mount, and the
  // History page loads the scan list.
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(async (url: string) => (
      Response.json(url === '/api/scans/' ? { scans: [] } : { status: 'ok' })
    )))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('redirects the root path to New Scan', () => {
    const router = renderAt('/')

    expect(screen.getByRole('heading', { name: 'New Scan' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/scan')
  })

  it('shows a nav link for every page', () => {
    renderAt('/scan')

    const nav = screen.getByRole('navigation', { name: 'Main' })
    for (const label of ['New Scan', 'Devices', 'Findings', 'History']) {
      expect(nav).toContainElement(screen.getByRole('link', { name: label }))
    }
  })

  it('navigates between pages and marks the current link', async () => {
    const user = userEvent.setup()
    renderAt('/scan')

    await user.click(screen.getByRole('link', { name: 'Findings' }))

    expect(screen.getByRole('heading', { name: 'Findings' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Findings' })).toHaveAttribute('aria-current', 'page')
    expect(screen.getByRole('link', { name: 'New Scan' })).not.toHaveAttribute('aria-current')
  })

  it.each([
    ['/devices', 'Devices'],
    ['/history', 'History'],
  ])('renders %s directly', (path, heading) => {
    renderAt(path)

    expect(screen.getByRole('heading', { name: heading })).toBeInTheDocument()
  })

  it('shows a not-found page for unknown paths', () => {
    renderAt('/nope')

    expect(screen.getByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Go to New Scan' })).toHaveAttribute('href', '/scan')
  })

  it('toggles the mobile menu', async () => {
    const user = userEvent.setup()
    renderAt('/scan')
    const button = screen.getByRole('button', { name: 'Menu' })

    expect(button).toHaveAttribute('aria-expanded', 'false')
    await user.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')
    await user.click(screen.getByRole('link', { name: 'Devices' }))
    expect(button).toHaveAttribute('aria-expanded', 'false')
  })
})
