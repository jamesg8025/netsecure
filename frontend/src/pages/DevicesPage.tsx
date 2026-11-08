import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import { SelectedScanHeading, SelectedScanMessage } from '../components/SelectedScan'
import { listScanDevices, type ScanDevice } from '../api/client'
import { useSelectedScan } from '../hooks/useSelectedScan'

const LOAD_ERROR = 'Could not load devices. Check that the backend is running.'

function deviceMatchesSearch(device: ScanDevice, query: string) {
  const searchText = [
    device.ip_address,
    device.hostname,
    device.port?.toString(),
    device.protocol,
    device.port !== null && device.protocol ? `${device.port}/${device.protocol}` : null,
    device.service,
    device.product,
    device.version,
  ].filter(Boolean).join(' ').toLowerCase()
  const searchTerms = query.split(/\s+/).filter(Boolean)

  return searchTerms.every((term) => searchText.includes(term))
}

function DevicesPage() {
  const [search, setSearch] = useState('')
  const selection = useSelectedScan(listScanDevices, LOAD_ERROR)

  const devices = selection.kind === 'ready' ? selection.data : []
  const query = search.trim().toLowerCase()
  const filteredDevices = devices.filter((device) => deviceMatchesSearch(device, query))
  const hostCount = new Set(filteredDevices.map((device) => device.host_id)).size

  return (
    <>
      <PageHeader
        title="Devices"
        description="Hosts a scan discovered, with their open ports and services. Shows the newest completed scan unless you choose one in History."
      />

      <section className="mt-6">
        {selection.kind !== 'ready' ? (
          <SelectedScanMessage selection={selection} noun="devices" />
        ) : (
          <>
            <SelectedScanHeading scan={selection.scan} />

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
