import { useState } from 'react'
import PageHeader from '../components/PageHeader'

type Severity = 'Low' | 'Medium' | 'High' | 'Critical'

type Finding = {
  id: number
  title: string
  description: string
  severity: Severity
  ip: string
  port: number
  service: string
}

const sampleFindings: Finding[] = [
  {
    id: 1,
    title: "Unencrypted HTTP Service",
    severity: "Medium",
    ip: "192.168.1.100",
    port: 80,
    service: "HTTP",
    description: "Web traffic may be transmitted without encryption"
  },
  {
    id: 2,
    title: "Weak Password Policy",
    severity: "High",
    ip: "192.168.1.101",
    port: 22,
    service: "SSH",
    description: "Password policy does not enforce complexity requirements"
  },
  {
    id: 3,
    title: "Insecure File Permissions",
    severity: "Medium",
    ip: "192.168.1.102",
    port: 21,
    service: "FTP",
    description: "Files are accessible with excessive permissions"
  },
  {
    id: 4,
    title: "Open Port",
    severity: "Critical",
    ip: "192.168.1.103",
    port: 445,
    service: "SMB",
    description: "Port is open and accessible from the internet"
  }
]

function FindingsPage() {
  const [search, setSearch] = useState('')
  const [severityFilter, setSeverityFilter] = useState ("All")

  const filteredFindings = sampleFindings.filter((finding) => {
    const matchesSearch = 
    `${finding.title} ${finding.ip} ${finding.service} ${finding.description}`
    .toLowerCase()
    .includes(search.toLowerCase())

    const matchesSeverity = severityFilter === "All" || finding.severity === severityFilter

    return matchesSearch && matchesSeverity
  })

  function getSeverityStyle(severity: Severity) {
    switch (severity) {
      case "Low":
        return { backgroundColor: "lightgreen", color: "darkgreen" }
      case "Medium":
        return { backgroundColor: "lightyellow", color: "darkgoldenrod" }
      case "High":
        return { backgroundColor: "lightcoral", color: "darkred" }
      case "Critical":
        return { backgroundColor: "lightpink", color: "darkmagenta" }
      default:
        return { backgroundColor: "lightgray", color: "black" }
    }
  }

  return (
    <>
      <PageHeader
        title="Findings"
        description="Security warnings generated from scan results, grouped by severity."
      />

      <section className='mt-6'>
        <div className='mb-4 flex flex-wrap items-center gap-3'>
          <input
            type="text"
            placeholder="Search findings..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border border-gray-300 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="border border-gray-300 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Severities</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </div>

        <p className = "mb-3 text-sm text-slate-600">
          {filteredFindings.length} finding(s) found
        </p>

        {filteredFindings.length === 0 ? (
          <p className = "rounded-md border border-slate-200 p-6 text-slate-600">
            No findings match your search.
          </p>
        ) : (
          <div className = "overflow-x-auto rounded-lg border border-slate-200">
            <table className = "w-full border-collapse text-left text-sm">
              <thead className = "bg-slate-100 text-slate-700">
                <tr>
                  <th className = "px-4 py-3">Severity</th>
                  <th className = "px-4 py-3">Finding</th>
                  <th className = "px-4 py-3">Host</th>
                  <th className = "px-4 py-3">Port</th>
                  <th className = "px-4 py-3">Description</th>
                </tr>
              </thead>

              <tbody className = "divide-y divide-slate-200">
                {filteredFindings.map((finding) => (
                  <tr key={finding.id} className = "hover:bg-slate-50">
                    <td className = "whitespace-nowrap px-4 py-3">
                      <span
                        className="inline-block rounded-full px-2 py-1 text-xs font-semibold"
                        style={getSeverityStyle(finding.severity)}
                      >
                        {finding.severity}
                      </span>
                    </td>
                    <td className = "px-4 py-3">{finding.title}</td>
                    <td className = "px-4 py-3">{finding.ip}</td>
                    <td className = "px-4 py-3">{finding.port}</td>
                    <td className = "px-4 py-3">{finding.description}</td>
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

export default FindingsPage
