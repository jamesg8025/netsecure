import type { ReactNode } from 'react'

type PlaceholderProps = {
  children: ReactNode
}

// Stand-in for page content that isn't built yet.
function Placeholder({ children }: PlaceholderProps) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
      {children}
    </div>
  )
}

export default Placeholder
