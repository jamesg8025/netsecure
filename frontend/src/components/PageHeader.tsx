type PageHeaderProps = {
  title: string
  description: string
}

function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-6">
      <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-1 text-sm text-slate-600">{description}</p>
    </div>
  )
}

export default PageHeader
