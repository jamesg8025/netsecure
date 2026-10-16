import { useState } from 'react'
import PageHeader from '../components/PageHeader'

type scanStatus = 'Completed' | 'Failed' | 'In-Progress'

type scanRecord = {
  id: number
  target: string
  timestamp: Date
  status: scanStatus
  devicesFound: number
  findingsFound: number
}

const sampleScans: scanRecord[] = [
  {
    id: 1,
    target: "192.168.1.1",
    timestamp: new Date(),
    status: "Completed",
    devicesFound: 5,
    findingsFound: 3
  },
  {
    id: 2,
    target: "10.0.0.1",
    timestamp: new Date(),
    status: "Failed",
    devicesFound: 0,
    findingsFound: 0
  },
  {
    id: 3,
    target: "172.16.0.1",
    timestamp: new Date(),
    status: "In-Progress",
    devicesFound: 2,
    findingsFound: 1
  }
]

function HistoryPage() {
  const [search, setSearch] = useState("")
  const [statusFilter, setstatusFilter] = useState('ALL')

  const filteredScans = sampleScans.filter(scan => {
    const matchesSearch = '${scan.target} ${scan.timestamp} ${scan.status}'.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === 'ALL' || scan.status === statusFilter
    return matchesSearch && matchesStatus
  })

  function getstatusStyle(status: scanStatus) {
    switch (status) {
      case 'Completed':
        return { backgroundColor: 'lightgreen', color: 'black' }
      case 'Failed':
        return { backgroundColor: 'lightcoral', color: 'black' }
      case 'In-Progress':
        return { backgroundColor: 'lightblue', color: 'black' }
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
        <div className= "mb-4 flex flex-wrrap items-center gap-3">
          <input
            type="text"
            placeholder="Search scans..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border border-gray-300 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => setstatusFilter(e.target.value)}
            className="border border-gray-300 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="Completed">Completed</option>
            <option value="Failed">Failed</option>
            <option value="In-Progress">In Progress</option>
          </select>
        </div>

        <p className = "mb-3 text-sm text-slate-600">
          {filteredScans.length} scan(s) found.
        </p>

        {filteredScans.length === 0 ? (
          <p className = "rounded-md border border-slate-200 p-6 text-slate-600">
            No scans match your search.
          </p>
        ) : (
          <div className = "overflow-x-auto rounded-lg border border-slate-200">
            <table className = "min-w-full divide-y divide-slate-200">
              <thead className = "bg-slate-100">
                <tr>
                  <th className = "px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Target</th>
                  <th className = "px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Timestamp</th>
                  <th className = "px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                  <th className = "px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Devices Found</th>
                  <th className = "px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Findings Found</th>
                </tr>
              </thead>
              <tbody className = "bg-white divide-y divide-slate-200">
                {filteredScans.map((scan) => (
                  <tr key={scan.id}>
                    <td className = "px-6 py-4 whitespace-nowrap">{scan.target}</td>
                    <td className = "px-6 py-4 whitespace-nowrap">{scan.timestamp.toLocaleString()}</td>
                    <td className = "px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-medium" style={getstatusStyle(scan.status)}>
                        {scan.status}
                      </span>
                    </td>
                    <td className = "px-6 py-4 whitespace-nowrap">{scan.devicesFound}</td>
                    <td className = "px-6 py-4 whitespace-nowrap">{scan.findingsFound}</td>
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
