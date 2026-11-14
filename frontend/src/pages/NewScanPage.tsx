import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import Spinner from '../components/Spinner'
import { startScan, type ScanResponse } from '../api/client'

// Formats whole seconds as m:ss (e.g. 65 -> "1:05").
function formatElapsed(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function NewScanPage() {
  const [target, setTarget] = useState('')
  const [scanTarget, setScanTarget] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [scanning, setScanning] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [result, setResult] = useState<ScanResponse | null>(null)

  // Scans are synchronous and report no progress, so count up the time since
  // the scan started to show the page hasn't frozen (NFR-02).
  useEffect(() => {
    if (!scanning) return
    const start = Date.now()
    const id = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000))
    }, 1000)
    return () => clearInterval(id)
  }, [scanning])

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (scanning) return

    setScanning(true)
    setScanTarget(target)
    setElapsed(0)
    setError('')
    setResult(null)
    setStatus('')
    try {
      const scan = await startScan(target)
      setResult(scan)
      const count = scan.hosts.length
      setStatus(`Scan of ${scan.target} complete: ${count} active host${count === 1 ? '' : 's'} found.`)
    } catch (err) {
      setStatus('')
      setError(err instanceof Error ? err.message : 'Scan failed.')
    } finally {
      setScanning(false)
    }
  }

  return (
    <>
      <PageHeader
        title="New Scan"
        description="Start a scan of an approved local network target."
      />
      
      <section className="mt-6 max-w-150">

        <form onSubmit={handleSubmit}>
          <div className="mb-5">
            <label 
            htmlFor="target"
            className="mb-2 block text-sm font-medium text-slate-700"
            >
              Target: IP Address or Network Range 
            </label>
            
            <input
              id="target"
              type="text"
              placeholder="e.g. 192.168.1.1 or 192.168.1.0/24"
              value={target}
              onChange={(e) => { 
                setTarget(e.target.value); 
                if (!scanning) {
                  setStatus('');
                  setError('');
                }
              }}
              required
              disabled={scanning}
              className = "w-full box-border rounded-md border border-slate-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-slate-100"
            />
          </div>

          <button 
          type="submit" 
          disabled={scanning}
          className="inline-flex cursor-pointer items-center gap-2 rounded-md bg-slate-900 px-5 py-2 text-white transition enabled:hover:bg-slate-800 active:scale-[0.97] disabled:cursor-wait disabled:opacity-70"
           >
            {scanning && <Spinner className="size-4 text-white" />}
            {scanning ? 'Scanning…' : 'Start Scan'}
          </button>
        </form>

        {scanning && (
          <div
            data-testid="scan-progress"
            className="mt-5 rounded-md border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900"
          >
            <div className="flex items-start gap-3">
              <Spinner className="mt-0.5 size-4 text-blue-600" />
              <p role="status" className="flex-1">
                Scanning <strong>{scanTarget}</strong>…{' '}
                <span className="block text-blue-700">This can take a few minutes.</span>
              </p>
              {/* Outside the status region so screen readers don't announce every tick. */}
              <span data-testid="scan-elapsed" className="tabular-nums text-blue-700">
                <span className="sr-only">Elapsed time </span>
                {formatElapsed(elapsed)}
              </span>
            </div>
            {/* Decorative; hidden under reduced motion, where the timer shows progress instead. */}
            <div
              aria-hidden="true"
              data-testid="scan-progress-bar"
              className="relative mt-3 h-1 overflow-hidden rounded-full bg-blue-100 motion-reduce:hidden"
            >
              <div className="absolute inset-y-0 left-0 w-1/4 rounded-full bg-blue-500 motion-safe:animate-indeterminate" />
            </div>
          </div>
        )}

        {status && (
          <p role="status" className="mt-5 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            {status}
          </p>
        )}

        {error && (
          <p role="alert" className="mt-5 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </p>
        )}

        {result && result.hosts.length > 0 && (
          <ul aria-label="Scan results" style={{ marginTop: '20px' }}>
            {result.hosts.map((host) => (
              <li key={host.ip} style={{ marginBottom: '16px' }}>
                <strong>{host.ip}</strong>
                {host.hostname && ` (${host.hostname})`}
                {host.services.length === 0 ? (
                  <p>No open services detected.</p>
                ) : (
                  <ul style={{ paddingLeft: '20px' }}>
                    {host.services.map((svc) => (
                      <li key={`${svc.protocol}/${svc.port}`}>
                        {svc.port}/{svc.protocol} {svc.service}
                        {(svc.product || svc.version) &&
                          ` — ${[svc.product, svc.version].filter(Boolean).join(' ')}`}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  )
}

export default NewScanPage
