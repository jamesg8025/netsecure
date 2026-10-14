import PageHeader from '../components/PageHeader'
import Placeholder from '../components/Placeholder'

function FindingsPage() {
  return (
    <>
      <PageHeader
        title="Findings"
        description="Security warnings generated from scan results, grouped by severity."
      />
      <Placeholder>Findings with severity indicators will go here.</Placeholder>
    </>
  )
}

export default FindingsPage
