import PageHeader from '../components/PageHeader'
import { useState } from 'react'

const sampleDevices = [
  {
    id: 1,
    Hostname: 'Device 1',
    ip: '192.168.1.1',
    ports: [22, 80],
    Services: ['SSH', 'HTTP'],
    product: ['OpenSSH', 'Apache httpd'],
    version: ['9.6p1', '2.4.58'],
  },
  {
    id: 2,
    Hostname: 'Device 2',
    ip: '192.168.1.2',
    ports: [443],
    Services: ['HTTPS'],
    product: ['nginx'],
    version: ['1.24.0'],
  },
  {
    id: 3,
    Hostname: 'Device 3',
    ip: '192.168.1.3',
    ports: [22, 3306],
    Services: ['SSH', 'MySQL'],
    product: ['OpenSSH', 'MySQL Server'],
    version: ['9.6p1', '8.0.36'],
  },
]

function DevicesPage() {
  const [search,setSearch] = useState('')

  const filteredDevices = sampleDevices.filter(device =>
    `${device.ip} ${device.Hostname} ${device.Services}`
    .toLowerCase()
    .includes(search.toLowerCase())
  )

  return (
    <>
      <PageHeader
        title="Devices"
        description="Hosts discovered by the most recent scan, with their open ports and services."
      />

     <section className="mt-6">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <input
            type="text"
            placeholder="Search by IP, hostname, or service..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-md rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p className="mb-3 text-sm text-slate-600">
          {filteredDevices.length} device(s) found
        </p>

        {filteredDevices.length === 0 ? (
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
                  <th className="px-4 py-3">Open Ports</th>
                  <th className="px-4 py-3">Services</th>
                  <th className="px-4 py-3">Product</th>
                  <th className="px-4 py-3">Version</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-200">
                {filteredDevices.map(device => (
                  <tr key={device.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-800">
                      {device.ip}
                    </td>
                    <td className="px-4 py-3">
                      {device.Hostname}
                    </td>
                    <td className="px-4 py-3">
                      {device.ports.join(', ')}
                    </td>
                    <td className="px-4 py-3">
                      {device.Services.join(', ')}
                    </td>
                    <td className="px-4 py-3">
                      {device.product.join(', ')}
                    </td>
                    <td className="px-4 py-3">
                      {device.version.join(', ')}
                    </td>
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

export default DevicesPage
