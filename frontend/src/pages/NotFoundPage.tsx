import { Link } from 'react-router'
import PageHeader from '../components/PageHeader'

function NotFoundPage() {
  return (
    <>
      <PageHeader title="Page not found" description="There's no page at this address." />
      <Link to="/scan" className="text-sm font-medium text-blue-600 hover:underline">
        Go to New Scan
      </Link>
    </>
  )
}

export default NotFoundPage
