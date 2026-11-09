import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router'
import { ApiError, login } from '../api/client'

const CONNECTION_ERROR = 'Could not reach NetSecure. Check that the backend is running and try again.'

function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  // Fields to mark aria-invalid: only the ones the current error is about.
  const [invalidFields, setInvalidFields] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting) return

    const missingFields: string[] = []
    if (!username.trim()) missingFields.push('username')
    if (!password) missingFields.push('password')
    if (missingFields.length > 0) {
      setError(`Enter your ${missingFields.join(' and ')}.`)
      setInvalidFields(missingFields)
      return
    }

    setError('')
    setInvalidFields([])
    setSubmitting(true)
    try {
      await login(username, password)
      navigate('/scan', { replace: true })
    } catch (cause: unknown) {
      if (cause instanceof ApiError && cause.status === 401) {
        setError('Incorrect username or password.')
        setInvalidFields(['username', 'password'])
      } else if (cause instanceof ApiError && cause.status === 403) {
        // A stale CSRF token (e.g. after logging in or out in another tab).
        // apiPost has already dropped it, so the next attempt gets a fresh one.
        setError('Your session changed. Please try again.')
      } else if (cause instanceof ApiError && cause.status < 500) {
        setError(cause.message)
      } else {
        setError(LOGIN_ERROR)
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12 text-slate-900">
      <section className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <header className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">NetSecure</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">Log in</h1>
          <p className="mt-2 text-sm text-slate-600">Sign in to continue to your dashboard.</p>
        </header>

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-5">
            <label htmlFor="username" className="mb-2 block text-sm font-medium text-slate-700">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(event) => {
                setUsername(event.target.value)
                setError('')
              }}
              disabled={submitting}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? 'login-error' : undefined}
              className="w-full rounded-md border border-slate-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
            />
          </div>

          <div className="mb-5">
            <label htmlFor="password" className="mb-2 block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value)
                setError('')
              }}
              disabled={submitting}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? 'login-error' : undefined}
              className="w-full rounded-md border border-slate-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
            />
          </div>

          {error && (
            <p id="login-error" role="alert" className="mb-5 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full cursor-pointer rounded-md bg-slate-900 px-5 py-2.5 font-medium text-white transition enabled:hover:bg-slate-800 disabled:cursor-wait disabled:opacity-70"
          >
            {submitting ? 'Logging in…' : 'Log in'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage
