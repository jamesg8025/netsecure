import { Navigate, type RouteObject } from 'react-router'
import DashboardLayout from './layouts/DashboardLayout'
import DevicesPage from './pages/DevicesPage'
import FindingsPage from './pages/FindingsPage'
import HistoryPage from './pages/HistoryPage'
import LoginPage from './pages/LoginPage'
import NewScanPage from './pages/NewScanPage'
import NotFoundPage from './pages/NotFoundPage'

// Kept separate from main.tsx so tests can mount the same routes in a memory router.
export const routes: RouteObject[] = [
  { path: '/login', element: <LoginPage /> },
  {
    path: '/',
    element: <DashboardLayout />,
    children: [
      { index: true, element: <Navigate to="/scan" replace /> },
      { path: 'scan', element: <NewScanPage /> },
      { path: 'devices', element: <DevicesPage /> },
      { path: 'findings', element: <FindingsPage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
