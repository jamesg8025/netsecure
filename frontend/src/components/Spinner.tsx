type SpinnerProps = {
  className?: string
}

// Decorative spinning ring. Hidden from screen readers, so put the loading
// text next to it. Size and color come from `className` (e.g. "size-4 text-white").
// Only spins when the user hasn't asked for reduced motion.
function Spinner({ className = 'size-4' }: SpinnerProps) {
  return (
    <svg
      aria-hidden="true"
      data-testid="spinner"
      viewBox="0 0 24 24"
      fill="none"
      className={`shrink-0 motion-safe:animate-spin ${className}`}
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
      <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
    </svg>
  )
}

export default Spinner
