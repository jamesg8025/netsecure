import { Link } from 'react-router'
import type { ScanSummary } from '../api/client'
import type { ScanSelection } from '../hooks/useSelectedScan'

type Pending = Exclude<ScanSelection<unknown>, { kind: 'ready' }>

const box = 'rounded-md border border-slate-200 p-6 text-slate-600'
const link = 'font-medium text-blue-600 hover:underline'

function formatTimestamp(timestamp: string | null) {
  return timestamp ? new Date(timestamp).toLocaleString() : 'an unknown time'
}

function HistoryLink() {
  return <Link to="/history" className={link}>Choose a scan in History</Link>
}

function whyNoResults(scan: ScanSummary) {
  switch (scan.status) {
    case 'Failed':
      return `failed${scan.error_message ? `: ${scan.error_message}` : '.'}`
    case 'In-Progress':
      return 'is still running.'
    default:
      return "hasn't started yet."
  }
}

// Everything a results page shows before it has a scan's results to list.
export function SelectedScanMessage({ selection, noun }: { selection: Pending; noun: string }) {
  switch (selection.kind) {
    case 'loading':
      return <p role="status" className={box}>Loading {noun}…</p>
    case 'error':
      return (
        <p role="alert" className="rounded-md border border-red-200 bg-red-50 p-6 text-red-700">
          {selection.message}
        </p>
      )
    case 'no-scan':
      return (
        <p className={box}>
          No completed scans yet. Run a scan from New Scan and its {noun} will appear here.
        </p>
      )
    case 'not-found':
      return (
        <p role="alert" className={box}>
          Scan #{selection.scanId} was not found. <HistoryLink />
        </p>
      )
    case 'unavailable':
      return (
        <p role="alert" className={box}>
          Scan #{selection.scan.scan_id} of {selection.scan.target} {whyNoResults(selection.scan)} It has
          no {noun} to show. <HistoryLink />
        </p>
      )
  }
}

// Names the scan whose results are listed below it.
export function SelectedScanHeading({ scan }: { scan: ScanSummary }) {
  return (
    <p className="mb-4 text-sm text-slate-600">
      Showing scan #{scan.scan_id} for {scan.target}, completed {formatTimestamp(scan.finished_at)}.{' '}
      <Link to="/history" className={link}>Choose a different scan</Link>
    </p>
  )
}
