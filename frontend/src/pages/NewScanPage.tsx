import { useState } from 'react'
import PageHeader from '../components/PageHeader'


function NewScanPage() {
  const [target, setTarget] = useState('')
  const [status, setStatus] = useState('')

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()

    setStatus(
      `Target ${target} is ready to scan. Backend integration pending.`
    )
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
                setStatus(''); 
              }}
              required
              style ={{
                width: '100%',
                padding: '10px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <button type="submit" style ={{
            padding: '10px 20px',
            backgroundColor: '#0f172a',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
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
            Start Scan
          </button>
        </form>

        {status && ( 
          <p role="status" style={{ marginTop: '20px' }}>
            {status}
          </p>
        )}
      </section>
    </>
  )
}

export default NewScanPage
