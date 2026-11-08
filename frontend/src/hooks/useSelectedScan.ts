import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { ApiError, listScans, type ScanSummary } from '../api/client'

// Which scan a results page (Devices, Findings) shows, and that scan's results.
export type ScanSelection<T> =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  // No ?scan= was given and no scan has completed yet.
  | { kind: 'no-scan' }
  // ?scan= names a scan that doesn't exist (UC-05 alternative path).
  | { kind: 'not-found'; scanId: string }
  // The chosen scan failed or hasn't finished, so it has no results.
  | { kind: 'unavailable'; scan: ScanSummary }
  | { kind: 'ready'; scan: ScanSummary; data: T }

export type ScanResultsLoader<T> = (scanId: number, signal: AbortSignal) => Promise<T>

/**
 * Loads the scan named by the `?scan=<id>` query parameter, or the newest
 * completed scan when there is none, then that scan's results.
 *
 * `loadResults` and `loadError` must be stable (module-level), since changing
 * them reloads.
 */
export function useSelectedScan<T>(loadResults: ScanResultsLoader<T>, loadError: string): ScanSelection<T> {
  const [searchParams] = useSearchParams()
  const requested = searchParams.get('scan')
  // Results are tagged with the request they answer, so a new ?scan= shows
  // loading instead of the previous scan's results.
  const [result, setResult] = useState<{ requested: string | null; selection: ScanSelection<T> } | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    const finish = (selection: ScanSelection<T>) => {
      if (!controller.signal.aborted) setResult({ requested, selection })
    }

    async function load() {
      try {
        // Newest first, so find() returns the newest completed scan.
        const scans = await listScans(controller.signal)
        const scan = requested === null
          ? scans.find((item) => item.status === 'Completed')
          : scans.find((item) => String(item.scan_id) === requested)

        if (!scan) {
          finish(requested === null ? { kind: 'no-scan' } : { kind: 'not-found', scanId: requested })
        } else if (scan.status !== 'Completed') {
          finish({ kind: 'unavailable', scan })
        } else {
          finish({ kind: 'ready', scan, data: await loadResults(scan.scan_id, controller.signal) })
        }
      } catch (err: unknown) {
        if (controller.signal.aborted) return
        // Only an ApiError with a code carries a message from the backend.
        const message = err instanceof ApiError && err.code ? err.message : loadError
        finish({ kind: 'error', message })
      }
    }

    void load()
    return () => controller.abort()
  }, [requested, loadResults, loadError])

  return result !== null && result.requested === requested ? result.selection : { kind: 'loading' }
}
