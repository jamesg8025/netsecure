import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { clearCsrfToken } from '../api/client'
import { AuthProvider } from '../auth/AuthContext'
import { routes } from '../routes'

function mockBackend(reply: Response | Promise<Response>) {
  const fetchMock = vi.fn<typeof fetch>(async (input) => {
    if (input === '/api/auth/me/') {
      return Response.json({ error: { code: 'not_authenticated' } }, { status: 401 })
    }
    if (input === '/api/csrf/') return Response.json({ csrfToken: 'csrf-before-login' })
    if (input === '/api/auth/login/') return await reply
    if (input === '/api/health/') return Response.json({ status: 'ok' })
    return new Response(null, { status: 404 })
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

async function renderLogin() {
  const router = createMemoryRouter(routes, { initialEntries: ['/login'] })
  render(<AuthProvider><RouterProvider router={router} /></AuthProvider>)
  await screen.findByRole('heading', { name: 'Log in' })
  return router
}

function loginSuccess() {
  return Response.json({
    user: { id: 4, username: 'izaiah' },
    csrfToken: 'csrf-after-login',
  })
}

describe('LoginPage (WBS 6.0/9.0, UC-01)', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    clearCsrfToken()
  })

  it.each([
    { username: '', password: '', error: 'Enter your username and password.' },
    { username: '', password: 'secret', error: 'Enter your username.' },
    { username: 'izaiah', password: '', error: 'Enter your password.' },
  ])('validates blank fields without sending credentials', async ({ username, password, error }) => {
    const user = userEvent.setup()
    const fetchMock = mockBackend(loginSuccess())
    await renderLogin()

    if (username) await user.type(screen.getByLabelText('Username'), username)
    if (password) await user.type(screen.getByLabelText('Password'), password)
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(screen.getByRole('alert')).toHaveTextContent(error)
    expect(fetchMock.mock.calls.map(([input]) => input)).toEqual(['/api/auth/me/'])
  })

  it('logs in and redirects to the dashboard', async () => {
    const user = userEvent.setup()
    const fetchMock = mockBackend(loginSuccess())
    const router = await renderLogin()

    await user.type(screen.getByLabelText('Username'), 'izaiah')
    await user.type(screen.getByLabelText('Password'), 'secret')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('heading', { name: 'New Scan' })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe('/scan')
    expect(fetchMock).toHaveBeenCalledWith('/api/auth/login/', expect.objectContaining({ method: 'POST' }))
  })

  it('shows the same credential error for an unsuccessful login', async () => {
    const user = userEvent.setup()
    mockBackend(Response.json(
      { error: { code: 'invalid_credentials', message: 'Incorrect username or password.' } },
      { status: 401 },
    ))
    await renderLogin()

    await user.type(screen.getByLabelText('Username'), 'izaiah')
    await user.type(screen.getByLabelText('Password'), 'wrong')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Incorrect username or password.')
    expect(screen.getByRole('heading', { name: 'Log in' })).toBeInTheDocument()
  })

  it('disables the form while the login request is pending', async () => {
    const user = userEvent.setup()
    let resolveLogin!: (response: Response) => void
    mockBackend(new Promise<Response>((resolve) => { resolveLogin = resolve }))
    await renderLogin()

    await user.type(screen.getByLabelText('Username'), 'izaiah')
    await user.type(screen.getByLabelText('Password'), 'secret')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(screen.getByRole('button', { name: 'Logging in…' })).toBeDisabled()
    expect(screen.getByLabelText('Username')).toBeDisabled()
    expect(screen.getByLabelText('Password')).toBeDisabled()

    resolveLogin(loginSuccess())
    expect(await screen.findByRole('heading', { name: 'New Scan' })).toBeInTheDocument()
  })

  it('shows a helpful message when the backend cannot be reached', async () => {
    const user = userEvent.setup()
    vi.stubGlobal('fetch', vi.fn<typeof fetch>(async (input) => {
      if (input === '/api/csrf/') return Response.json({ csrfToken: 'csrf-before-login' })
      throw new TypeError('Failed to fetch')
    }))
    await renderLogin()

    await user.type(screen.getByLabelText('Username'), 'izaiah')
    await user.type(screen.getByLabelText('Password'), 'secret')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Could not reach NetSecure. Check that the backend is running and try again.',
    )
  })
})
