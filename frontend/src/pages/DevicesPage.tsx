import { useState } from 'react'
import PageHeader from '../components/PageHeader'

type Service = {
  port: number
  name: string
  product: string
  version: string
}

type Device = {
  id: number
  hostname: string
  ip: string
  services: Service[]
}

const sampleDevices: Device[] = [
  {
    id: 1,
    hostname: 'Device 1',
    ip: '192.168.1.1',
    services: [
      { port: 22, name: 'SSH', product: 'OpenSSH', version: '9.6p1' },
      { port: 80, name: 'HTTP', product: 'Apache httpd', version: '2.4.58' },
    ],
  },
  {
    id: 2,
    hostname: 'Device 2',
    ip: '192.168.1.2',
    services: [{ port: 443, name: 'HTTPS', product: 'nginx', version: '1.24.0' }],
  },
  {
    id: 3,
    hostname: 'Device 3',
    ip: '192.168.1.3',
    services: [
      { port: 22, name: 'SSH', product: 'OpenSSH', version: '9.6p1' },
      { port: 3306, name: 'MySQL', product: 'MySQL Server', version: '8.0.36' },
    ],
  },
]

function DevicesPage() {
  const [search, setSearch] = useState('')
  const query = search.trim().toLowerCase()

  const filteredDevices = sampleDevices.flatMap((device) => {
    const hostMatches = `${device.ip} ${device.hostname}`.toLowerCase().includes(query)
    const services = query === '' || hostMatches
      ? device.services
      : device.services.filter((service) =>
          `${service.port} ${service.name} ${service.product} ${service.version}`
            .toLowerCase()
            .includes(query),
        )

    return hostMatches || services.length > 0 ? [{ ...device, services }] : []
  })

  const serviceRows = filteredDevices.flatMap((device) =>
    device.services.map((service) => ({ device, service })),
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
            placeholder="Search by IP, hostname, service, product, or version..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-md rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p className="mb-3 text-sm text-slate-600">
          {filteredDevices.length} device(s) found
        </p>

        {serviceRows.length === 0 ? (
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
                {serviceRows.map(({ device, service }) => (
                  <tr key={`${device.id}-${service.port}`} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-800">
                      {device.ip}
                    </td>
                    <td className="px-4 py-3">{device.hostname}</td>
                    <td className="px-4 py-3">{service.port}</td>
                    <td className="px-4 py-3">{service.name}</td>
                    <td className="px-4 py-3">{service.product}</td>
                    <td className="px-4 py-3">{service.version}</td>
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
