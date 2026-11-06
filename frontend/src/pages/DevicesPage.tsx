import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { ApiError, listScanDevices, listScans, type ScanDevice, type ScanSummary } from '../api/client'

type LoadState =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'no-scan' }
  | { kind: 'ready'; scan: ScanSummary; devices: ScanDevice[] }

const LOAD_ERROR = 'Could not load devices. Check that the backend is running.'

function formatTimestamp(timestamp: string | null) {
  return timestamp ? new Date(timestamp).toLocaleString() : 'Unknown time'
}

function deviceMatchesSearch(device: ScanDevice, query: string) {
  const searchText = [
    device.ip_address,
    device.hostname,
    device.port?.toString(),
    device.protocol,
    device.service,
    device.product,
    device.version,
  ].filter(Boolean).join(' ').toLowerCase()

  return searchText.includes(query)
}

function DevicesPage() {
  const [search, setSearch] = useState('')
  const [load, setLoad] = useState<LoadState>({ kind: 'loading' })

  useEffect(() => {
    const controller = new AbortController()

    async function loadLatestDevices() {
      try {
        const scans = await listScans(controller.signal)
        // History is newest first. Skip pending/failed scans and show the
        // newest scan whose results are complete.
        const scan = scans.find((item) => item.status === 'Completed')
        if (!scan) {
          setLoad({ kind: 'no-scan' })
          return
        }

        const devices = await listScanDevices(scan.scan_id, controller.signal)
        setLoad({ kind: 'ready', scan, devices })
      } catch (err: unknown) {
        if (controller.signal.aborted) return
        const message = err instanceof ApiError && err.code ? err.message : LOAD_ERROR
        setLoad({ kind: 'error', message })
      }
    }

    void loadLatestDevices()
    return () => controller.abort()
  }, [])

  const devices = load.kind === 'ready' ? load.devices : []
  const query = search.trim().toLowerCase()
  const filteredDevices = devices.filter((device) => deviceMatchesSearch(device, query))
  const hostCount = new Set(filteredDevices.map((device) => device.host_id)).size

  return (
    <>
      <PageHeader
        title="Devices"
        description="Hosts discovered by the most recent completed scan, with their open ports and services."
      />

      <section className="mt-6">
        {load.kind === 'loading' ? (
          <p role="status" className="rounded-md border border-slate-200 p-6 text-slate-600">
            Loading devices…
          </p>
        ) : load.kind === 'error' ? (
          <p role="alert" className="rounded-md border border-red-200 bg-red-50 p-6 text-red-700">
            {load.message}
          </p>
        ) : load.kind === 'no-scan' ? (
          <p className="rounded-md border border-slate-200 p-6 text-slate-600">
            No completed scans yet. Run a scan from New Scan and its devices will appear here.
          </p>
        ) : (
          <>
            <p className="mb-4 text-sm text-slate-600">
              Showing scan #{load.scan.scan_id} for {load.scan.target}, completed {formatTimestamp(load.scan.finished_at)}.
            </p>

            <div className="mb-4 flex flex-wrap items-center gap-3">
              <input
                type="text"
                placeholder="Search by IP, hostname, service, product, or version..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full max-w-md rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <p className="mb-3 text-sm text-slate-600">
              {hostCount} device{hostCount === 1 ? '' : 's'} found · {filteredDevices.length} row{filteredDevices.length === 1 ? '' : 's'} shown
            </p>

            {devices.length === 0 ? (
              <p className="rounded-md border border-slate-200 p-6 text-slate-600">
                No devices were found in this scan.
              </p>
            ) : filteredDevices.length === 0 ? (
              <p className="rounded-md border border-slate-200 p-6 text-slate-600">
                No devices match your search.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-200">
                <table className="w-full border-collapse text-left text-sm">
                  <thead className="bg-slate-100 text-slate-700">
                    <tr>
                      <th className="px-4 py-3">IP Address</th>
                      <th className="px-4 py-3">Hostname</th>
                      <th className="px-4 py-3">Open Port</th>
                      <th className="px-4 py-3">Service</th>
                      <th className="px-4 py-3">Product</th>
                      <th className="px-4 py-3">Version</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {filteredDevices.map((device) => (
                      <tr
                        key={`${device.host_id}-${device.port ?? 'no-port'}-${device.protocol ?? 'no-protocol'}`}
                        className="hover:bg-slate-100"
                      >
                        <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-800">
                          {device.ip_address}
                        </td>
                        <td className="px-4 py-3">{device.hostname || '—'}</td>
                        <td className="px-4 py-3">
                          {device.port === null ? '—' : `${device.port}${device.protocol ? `/${device.protocol}` : ''}`}
                        </td>
                        <td className="px-4 py-3">{device.service || '—'}</td>
                        <td className="px-4 py-3">{device.product || '—'}</td>
                        <td className="px-4 py-3">{device.version || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>
    </>
  )
}

export default DevicesPage
