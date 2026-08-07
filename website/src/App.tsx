import { useEffect, useState } from 'react'
import Header from './components/Header'
import Footer from './components/Footer'
import EmailForm from './components/EmailForm/EmailForm'
import AnalyticsDashboard from './pages/AnalyticsDashboard'

export type AppPage = 'send' | 'analytics'

function pageFromHash(): AppPage {
  const hash = window.location.hash.replace(/^#/, '')
  return hash === 'analytics' ? 'analytics' : 'send'
}

export default function App() {
  const [page, setPage] = useState<AppPage>(pageFromHash)

  useEffect(() => {
    const onHash = () => setPage(pageFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const navigate = (next: AppPage) => {
    window.location.hash = next === 'analytics' ? 'analytics' : 'send'
    setPage(next)
  }

  return (
    <div className="app-shell">
      <Header page={page} onNavigate={navigate} />
      <main className="app-main">
        {page === 'analytics' ? <AnalyticsDashboard /> : <EmailForm />}
      </main>
      <Footer />
    </div>
  )
}
