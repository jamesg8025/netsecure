import PageHeader from '../components/PageHeader'
import Placeholder from '../components/Placeholder'

function DevicesPage() {
  return (
    <>
      <PageHeader
        title="Devices"
        description="Hosts discovered by the most recent scan, with their open ports and services."
      />
      <Placeholder>The device list will go here.</Placeholder>
    </>
  )
}

export default DevicesPage
