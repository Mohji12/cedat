import './LoaderModal.css'

type LoaderModalProps = {
  show: boolean
}

export default function LoaderModal({ show }: LoaderModalProps) {
  if (!show) return null

  return (
    <div className="modal-backdrop" role="status" aria-live="polite" aria-busy="true">
      <div className="modal-loader">
        <div className="cedat-loader">
          <span className="cedat-loader-ring" aria-hidden="true" />
          <span className="cedat-loader-pulse" aria-hidden="true" />
          <img
            className="cedat-loader-logo"
            src="/cedat-logo.png"
            alt=""
            decoding="async"
          />
        </div>
        <p className="loader-text">Sending emails, please wait...</p>
        <div className="loader-dots" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  )
}
