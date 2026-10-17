import PageHeader from '../components/PageHeader'
import { useState } from 'react'

const sampleDevices = [
  { id: 1, Hostname: 'Device 1', ip: '192.168.1.1', ports: [22, 80], Services: ['SSH', 'HTTP'] },
  { id: 2, Hostname: 'Device 2', ip: '192.168.1.2', ports: [443], Services: ['HTTPS'] },
  { id: 3, Hostname: 'Device 3', ip: '192.168.1.3', ports: [22, 3306], Services: ['SSH', 'MySQL'] },
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

      <section>
        
        <input
          type="text"
          placeholder="Search by IP, hostname, or service..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ marginBottom: '20px' }}
        />

        {filteredDevices.length === 0 ? (
          <p>No devices match your search.</p>
        ) : (
          <table style = {{ width: '100%', borderCollapse: 'collapse', marginTop:'10px'}}>
            <thead>
              <tr>
                <th style={{ width: '25%', padding: '12px', textAlign: 'left' }}>IP Address</th>
                <th style={{ width: '25%', padding: '12px', textAlign: 'left' }}>Hostname</th>
                <th style={{ width: '25%', padding: '12px', textAlign: 'left' }}>Open Ports</th>
                <th style={{ width: '25%', padding: '12px', textAlign: 'left' }}>Services</th>
              </tr>
            </thead>
            <tbody>
              {filteredDevices.map(device => (
                <tr key={device.ip}>
                  <td style={{ padding: '12px' }}>{device.ip}</td>
                  <td style={{ padding: '12px' }}>{device.Hostname}</td>
                  <td style={{ padding: '12px' }}>{device.ports}</td>
                  <td style={{ padding: '12px' }}>{device.Services.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <p>{filteredDevices.length} device(s) found</p>

      </section>
    </>
  )
}

export default DevicesPage
