import { useState } from 'react'
import { NavLink, Outlet } from 'react-router'
import BackendStatus from '../components/BackendStatus'

const navItems = [
  { to: '/scan', label: 'New Scan' },
  { to: '/devices', label: 'Devices' },
  { to: '/findings', label: 'Findings' },
  { to: '/history', label: 'History' },
]

function DashboardLayout() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 md:flex">
      <aside className="bg-slate-900 text-slate-100 md:w-56 md:shrink-0">
        <div className="flex items-center justify-between px-4 py-3 md:py-5">
          <h1 className="text-lg font-semibold tracking-tight">NetSecure</h1>
          <button
            type="button"
            className="rounded px-2 py-1 text-sm text-slate-300 hover:bg-slate-800 md:hidden"
            aria-controls="main-nav"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            Menu
          </button>
        </div>
        <nav
          id="main-nav"
          aria-label="Main"
          className={`${menuOpen ? 'block' : 'hidden'} px-2 pb-3 md:block`}
        >
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) =>
                    `block rounded px-3 py-2 text-sm ${
                      isActive
                        ? 'bg-slate-800 font-medium text-white'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-end border-b border-slate-200 bg-white px-6 py-3">
          <BackendStatus />
        </header>
        <main className="flex-1 px-6 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
