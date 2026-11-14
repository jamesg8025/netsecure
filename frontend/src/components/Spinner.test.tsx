import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import Spinner from './Spinner'

describe('Spinner', () => {
  it('is hidden from screen readers and only spins when motion is allowed', () => {
    render(<Spinner />)

    const spinner = screen.getByTestId('spinner')
    expect(spinner).toHaveAttribute('aria-hidden', 'true')
    expect(spinner).toHaveClass('motion-safe:animate-spin', 'size-4')
  })

  it('takes size and color from className', () => {
    render(<Spinner className="size-5 text-white" />)

    expect(screen.getByTestId('spinner')).toHaveClass('size-5', 'text-white')
  })
})
