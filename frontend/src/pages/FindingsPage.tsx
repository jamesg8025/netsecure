import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import { SelectedScanHeading, SelectedScanMessage } from '../components/SelectedScan'
import { listScanFindings, type FindingSeverity, type ScanFinding } from '../api/client'
import { useSelectedScan } from '../hooks/useSelectedScan'

const LOAD_ERROR = 'Could not load findings. Check that the backend is running.'

// Most severe first, matching the API's order.
const SEVERITIES: { value: FindingSeverity; label: string; style: { backgroundColor: string; color: string } }[] = [
  { value: 'critical', label: 'Critical', style: { backgroundColor: 'lightpink', color: 'darkmagenta' } },
  { value: 'high', label: 'High', style: { backgroundColor: 'lightcoral', color: 'darkred' } },
  { value: 'medium', label: 'Medium', style: { backgroundColor: 'lightyellow', color: 'darkgoldenrod' } },
  { value: 'low', label: 'Low', style: { backgroundColor: 'lightgreen', color: 'darkgreen' } },
  { value: 'info', label: 'Info', style: { backgroundColor: 'lightgray', color: 'black' } },
]

function severityOf(value: FindingSeverity) {
  return SEVERITIES.find((severity) => severity.value === value) ?? SEVERITIES[SEVERITIES.length - 1]
}

function findingMatchesSearch(finding: ScanFinding, terms: string[]) {
  const searchText = [
    finding.finding,
    finding.host,
    finding.port.toString(),
    finding.protocol,
    `${finding.port}/${finding.protocol}`,
    finding.service,
    finding.description,
  ].filter(Boolean).join(' ').toLowerCase()

  return terms.every((term) => searchText.includes(term))
}

function FindingsPage() {
  const [search, setSearch] = useState('')
  const [severityFilter, setSeverityFilter] = useState('All')
  const selection = useSelectedScan(listScanFindings, LOAD_ERROR)

  const findings = selection.kind === 'ready' ? selection.data : []
  const searchTerms = search.trim().toLowerCase().split(/\s+/).filter(Boolean)
  const filteredFindings = findings.filter((finding) => (
    findingMatchesSearch(finding, searchTerms)
    && (severityFilter === 'All' || finding.severity === severityFilter)
  ))

  return (
    <>
      <PageHeader
        title="Findings"
        description="Security warnings generated from scan results, most severe first. Shows the newest completed scan unless you choose one in History."
      />

      <section className='mt-6'>
        {selection.kind !== 'ready' ? (
          <SelectedScanMessage selection={selection} noun="findings" />
        ) : findings.length === 0 ? (
          <>
            <SelectedScanHeading scan={selection.scan} />
            <p className="rounded-md border border-slate-200 p-6 text-slate-600">
              No findings for this scan. This doesn't mean the network is safe.
              Scans saved before service checks were added have no generated findings; run a new scan to apply them.
            </p>
          </>
        ) : (
          <>
            <SelectedScanHeading scan={selection.scan} />

            <p className="mb-4 text-sm text-slate-600">
              These are service-review warnings, not confirmed vulnerabilities. Authentication,
              exploitation, and CVE checks were not performed.
            </p>

            <div className='mb-4 flex flex-wrap items-center gap-3'>
              <input
                type="text"
                placeholder="Search findings..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full max-w-md rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                aria-label="Severity"
                className="rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">All Severities</option>
                {SEVERITIES.map((severity) => (
                  <option key={severity.value} value={severity.value}>{severity.label}</option>
                ))}
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
                      <th className = "px-4 py-3">Service</th>
                      <th className = "px-4 py-3">Description</th>
                    </tr>
                  </thead>

                  <tbody className = "divide-y divide-slate-200">
                    {filteredFindings.map((finding) => {
                      const severity = severityOf(finding.severity)
                      return (
                        <tr key={finding.finding_id} className = "hover:bg-slate-100">
                          <td className = "whitespace-nowrap px-4 py-3">
                            <span
                              className="inline-block rounded-full px-2 py-1 text-xs font-semibold"
                              style={severity.style}
                            >
                              {severity.label}
                            </span>
                          </td>
                          <td className = "px-4 py-3">{finding.finding}</td>
                          <td className = "px-4 py-3">{finding.host}</td>
                          <td className = "whitespace-nowrap px-4 py-3">{finding.port}/{finding.protocol}</td>
                          <td className = "px-4 py-3">{finding.service || '—'}</td>
                          <td className = "px-4 py-3">{finding.description}</td>
                        </tr>
                      )
                    })}
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

export default FindingsPage
