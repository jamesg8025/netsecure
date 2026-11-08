import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import FindingsPage from './FindingsPage'

describe('FindingsPage', () => {
  it('shows each finding service in the Service column', () => {
    render(<FindingsPage />)

    expect(screen.getByRole('columnheader', { name: 'Service' })).toBeInTheDocument()
    const firstFinding = screen.getAllByRole('row')[1]
    const cells = within(firstFinding).getAllByRole('cell')
    expect(cells[4]).toHaveTextContent('HTTP')
  })

  it('searches by port and trims surrounding whitespace', async () => {
    const user = userEvent.setup()
    render(<FindingsPage />)

    await user.type(screen.getByPlaceholderText('Search findings...'), ' 445 ')

    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(2)
    expect(within(rows[1]).getAllByRole('cell').map((cell) => cell.textContent)).toEqual([
      'Critical', 'Open Port', '192.168.1.103', '445', 'SMB', 'Port is open and accessible from the internet',
    ])
  })
})
