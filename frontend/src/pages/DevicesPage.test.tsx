import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import DevicesPage from './DevicesPage'

describe('DevicesPage (WBS 6.0)', () => {
  it('keeps each port, service, product, and version together in one row', () => {
    render(<DevicesPage />)

    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(6)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.1', 'Device 1', '22', 'SSH', 'OpenSSH', '9.6p1',
    ])
    expect(within(rows[2]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.1', 'Device 1', '80', 'HTTP', 'Apache httpd', '2.4.58',
    ])
  })

  it('searches products and versions and shows the matching service row', async () => {
    const user = userEvent.setup()
    render(<DevicesPage />)

    const search = screen.getByPlaceholderText(/search by ip, hostname, service, product, or version/i)
    await user.type(search, 'apache httpd')

    let rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(2)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.1', 'Device 1', '80', 'HTTP', 'Apache httpd', '2.4.58',
    ])

    await user.clear(search)
    await user.type(search, '8.0.36')

    rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(2)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      '192.168.1.3', 'Device 3', '3306', 'MySQL', 'MySQL Server', '8.0.36',
    ])
  })
})
