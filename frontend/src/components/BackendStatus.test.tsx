import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import BackendStatus from './BackendStatus'

function stubFetch(impl: () => Promise<Response>) {
  const fetchMock = vi.fn(impl)
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('BackendStatus', () => {
  it('shows connected when the health check returns ok', async () => {
    const fetchMock = stubFetch(async () => Response.json({ status: 'ok' }))

    render(<BackendStatus />)

    expect(screen.getByRole('status')).toHaveTextContent('Backend: Checking…')
    expect(await screen.findByText(/Connected/)).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/health/', expect.anything())
  })

  it('shows unreachable when the backend returns an error status', async () => {
    stubFetch(async () => new Response(null, { status: 502 }))

    render(<BackendStatus />)

    expect(await screen.findByText(/Unreachable/)).toBeInTheDocument()
  })

  it('shows unreachable when the request fails', async () => {
    stubFetch(async () => {
      throw new TypeError('Failed to fetch')
    })

    render(<BackendStatus />)

    expect(await screen.findByText(/Unreachable/)).toBeInTheDocument()
  })
})
