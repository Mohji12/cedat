import type { AppPage } from '../App'

type HeaderProps = {
  page: AppPage
  onNavigate: (page: AppPage) => void
}

export default function Header({ page, onNavigate }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="app-header-inner">
        <button
          type="button"
          className="app-header-brand-btn"
          onClick={() => onNavigate('send')}
          aria-label="CEDAT home"
        >
          <img
            className="app-header-logo"
            src="/cedat-logo.png"
            alt="CEDAT"
            decoding="async"
          />
          <div className="app-header-copy">
            <p className="app-header-brand">CEDAT</p>
            <p className="app-header-tagline">Bulk Email</p>
          </div>
        </button>

        <nav className="app-nav" aria-label="Primary">
          <button
            type="button"
            className={`app-nav-link${page === 'send' ? ' is-active' : ''}`}
            aria-current={page === 'send' ? 'page' : undefined}
            onClick={() => onNavigate('send')}
          >
            Send
          </button>
          <button
            type="button"
            className={`app-nav-link${page === 'analytics' ? ' is-active' : ''}`}
            aria-current={page === 'analytics' ? 'page' : undefined}
            onClick={() => onNavigate('analytics')}
          >
            Analytics
          </button>
        </nav>
      </div>
    </header>
  )
}
