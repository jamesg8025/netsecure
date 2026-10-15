import { useEffect, useState } from 'react'
import { getHealth } from '../api/client'

type Status = 'checking' | 'connected' | 'unreachable'

const POLL_INTERVAL_MS = 30_000

const display: Record<Status, { label: string; dot: string }> = {
  checking: { label: 'Checking…', dot: 'bg-slate-400' },
  connected: { label: 'Connected', dot: 'bg-emerald-500' },
  unreachable: { label: 'Unreachable', dot: 'bg-red-500' },
}

// Shows whether the Django backend answers GET /api/health/.
function BackendStatus() {
  const [status, setStatus] = useState<Status>('checking')

  useEffect(() => {
    const controller = new AbortController()

    const check = () => {
      getHealth(controller.signal)
        .then((health) => setStatus(health.status === 'ok' ? 'connected' : 'unreachable'))
        .catch(() => {
          if (!controller.signal.aborted) setStatus('unreachable')
        })
    }

    check()
    const timer = setInterval(check, POLL_INTERVAL_MS)
    return () => {
      controller.abort()
      clearInterval(timer)
    }
  }, [])

  const { label, dot } = display[status]
  return (
    <p role="status" className="flex items-center gap-2 text-sm text-slate-600">
      <span aria-hidden="true" className={`h-2 w-2 rounded-full ${dot}`} />
      Backend: {label}
    </p>
  )
}

export default BackendStatus
