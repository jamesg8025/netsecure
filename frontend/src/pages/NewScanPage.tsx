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
      
      <section style={{ maxWidth: '600px', marginTop: '24px' }}>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label 
            htmlFor="target"
            style={{ display: 'block', marginBottom: '8px' }}
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
              style ={{
                width: '100%',
                padding: '10px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <button type="submit" disabled={scanning} style ={{
            padding: '10px 20px',
            backgroundColor: '#0f172a',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: scanning ? 'wait' : 'pointer',
            opacity: scanning ? 0.7 : 1,
            transition: 'background-color 0.15s, transform 0.1s',
           }}
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
          <p role="status" style={{ marginTop: '20px' }}>
            {status}
          </p>
        )}

        {error && (
          <p role="alert" style={{ marginTop: '20px', color: '#b91c1c' }}>
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
