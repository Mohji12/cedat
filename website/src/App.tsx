import './App.css'
import EmailForm from './components/EmailForm'

export default function App() {
  return (
    <>
      <div className="app-shell">
        <a className="brand-logo-card" href="/" aria-label="CEDAT">
          <img
            className="brand-logo"
            src="/cedat-logo.png"
            alt="CEDAT"
            loading="lazy"
            decoding="async"
          />
        </a>
        <div className="form-bg-wrapper">
          <EmailForm />
        </div>
      </div>
      <footer className="footer-powered">
        Powered By <span className="footer-brand">Biogred</span>
      </footer>
    </>
  )
}
