import { useEffect, useState, type ReactNode } from 'react'
import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
  SESSION_EXPIRED_EVENT,
} from '../api/client'
import { AuthContext } from './context'
import type { AuthUser } from '../api/client'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    const onSessionExpired = () => {
      setUser(null)
      setLoading(false)
    }

    window.addEventListener(SESSION_EXPIRED_EVENT, onSessionExpired)
    getCurrentUser()
      .then((currentUser) => {
        if (active) setUser(currentUser)
      })
      .catch(() => {
        if (active) setUser(null)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
      window.removeEventListener(SESSION_EXPIRED_EVENT, onSessionExpired)
    }
  }, [])

  async function login(username: string, password: string) {
    const response = await loginRequest(username, password)
    setUser(response.user)
    setLoading(false)
    return response.user
  }

  async function logout() {
    await logoutRequest()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
