import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import { startScan, type ScanResponse } from '../api/client'


function NewScanPage() {
  const [target, setTarget] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [scanning, setScanning] = useState(false)
  const [result, setResult] = useState<ScanResponse | null>(null)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (scanning) return

    setScanning(true)
    setError('')
    setResult(null)
    setStatus(`Scanning ${target}… this can take a few minutes.`)
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
          className = "rounded-md bg-slate-900 px-5 py-2 text-white transition-colors hover:bg-slate-800 disabled:cursor-wait disabled:opacity-70"
           
           onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#1e293b';
           }}
           onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#0f172a';
            e.currentTarget.style.transform = 'scale(1)';
           }}
           onMouseDown={(e) => {
            e.currentTarget.style.backgroundColor = '#334155';
            e.currentTarget.style.transform = 'scale(0.97)';
           }}
           onMouseUp={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
           }}
           >
            {scanning ? 'Scanning…' : 'Start Scan'}
          </button>
        </form>

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
