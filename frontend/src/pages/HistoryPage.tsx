import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { ApiError, listScans, type ScanStatus, type ScanSummary } from '../api/client'

type LoadState =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'ready'; scans: ScanSummary[] }

const LOAD_ERROR = 'Could not load scan history. Check that the backend is running.'

// A scan that never started has no timestamp.
function formatTimestamp(timestamp: string | null) {
  return timestamp ? new Date(timestamp).toLocaleString() : 'Not started'
}

function HistoryPage() {
  const [search, setSearch] = useState("")
  const [statusFilter, setstatusFilter] = useState('ALL')
  const [load, setLoad] = useState<LoadState>({ kind: 'loading' })

  useEffect(() => {
    const controller = new AbortController()

    listScans(controller.signal)
      .then((scans) => setLoad({ kind: 'ready', scans }))
      .catch((err: unknown) => {
        if (controller.signal.aborted) return
        // Only an ApiError with a code carries a message from the backend.
        const message = err instanceof ApiError && err.code ? err.message : LOAD_ERROR
        setLoad({ kind: 'error', message })
      })

    return () => controller.abort()
  }, [])

  const scans = load.kind === 'ready' ? load.scans : []

  const filteredScans = scans.filter(scan => {
    const matchesSearch = `${scan.target} ${formatTimestamp(scan.timestamp)} ${scan.status}`.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === 'ALL' || scan.status === statusFilter
    return matchesSearch && matchesStatus
  })

  function getstatusStyle(status: ScanStatus) {
    switch (status) {
      case 'Completed':
        return { backgroundColor: 'lightgreen', color: 'black' }
      case 'Failed':
        return { backgroundColor: 'lightcoral', color: 'black' }
      case 'In-Progress':
        return { backgroundColor: 'lightblue', color: 'black' }
      case 'Pending':
      default:
        return { backgroundColor: 'lightgray', color: 'black' }
    }
  }

  return (
    <>
      <PageHeader
        title="History"
        description="Past scans and their results."
      />

      <section className= "mt-6">
        <div className= "mb-4 flex flex-wrap items-center gap-3">
          <input
            type="text"
            placeholder="Search scans..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-md rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => setstatusFilter(e.target.value)}
            className="rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="Completed">Completed</option>
            <option value="Failed">Failed</option>
            <option value="In-Progress">In Progress</option>
            <option value="Pending">Pending</option>
          </select>
        </div>

        {scans.length > 0 && (
          <p className = "mb-3 text-sm text-slate-600">
            {filteredScans.length} scan(s) found.
          </p>
        )}

        {load.kind === 'loading' ? (
          <p role="status" className = "rounded-md border border-slate-200 p-6 text-slate-600">
            Loading scans…
          </p>
        ) : load.kind === 'error' ? (
          <p role="alert" className = "rounded-md border border-red-200 bg-red-50 p-6 text-red-700">
            {load.message}
          </p>
        ) : scans.length === 0 ? (
          <p className = "rounded-md border border-slate-200 p-6 text-slate-600">
            No scans yet. Run one from New Scan and it will appear here.
          </p>
        ) : filteredScans.length === 0 ? (
          <p className = "rounded-md border border-slate-200 p-6 text-slate-600">
            No scans match your search.
          </p>
        ) : (
          <div className = "overflow-x-auto rounded-lg border border-slate-200">
            <table className = "w-full border-collapse text-left text-sm">
              <thead className="bg-slate-100 text-slate-700">
                <tr>
                  <th className="px-4 py-3">Target</th>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Devices Found</th>
                  <th className="px-4 py-3">Findings Found</th>
                </tr>
              </thead>
              <tbody className = "divide-y divide-slate-200">
                {filteredScans.map((scan) => (
                  <tr key={scan.scan_id}>
                    <td className = "px-4 py-3 whitespace-nowrap">{scan.target}</td>
                    <td className = "px-4 py-3 whitespace-nowrap">{formatTimestamp(scan.timestamp)}</td>
                    <td className = "px-4 py-3 whitespace-nowrap">
                      <span className="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-medium" style={getstatusStyle(scan.status)}>
                        {scan.status}
                      </span>
                      {scan.error_message && (
                        <p className = "mt-1 max-w-xs whitespace-normal text-xs text-slate-600">{scan.error_message}</p>
                      )}
                    </td>
                    <td className = "px-4 py-3 whitespace-nowrap">{scan.devices_found}</td>
                    <td className = "px-4 py-3 whitespace-nowrap">{scan.findings_found}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      </section>
    </>
  )
}

export default HistoryPage
