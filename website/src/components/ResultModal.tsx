import { useEffect, useRef } from 'react'
import type { SendResult } from '../types/email'
import './ResultModal.css'

type ResultModalProps = {
  result: SendResult | null
  onClose: () => void
}

export default function ResultModal({ result, onClose }: ResultModalProps) {
  const closeRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!result) return

    closeRef.current?.focus()

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [result, onClose])

  if (!result) return null

  const { emails_sent, emails_failed, emails_total } = result
  const allFailed = emails_total > 0 && emails_sent === 0
  const partial = emails_failed > 0 && emails_sent > 0
  const title = allFailed
    ? 'No emails were sent'
    : partial
      ? 'Emails partially sent'
      : 'Emails sent successfully'

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="result-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="modal-result">
        <img className="result-logo" src="/cedat-logo.png" alt="" decoding="async" />
        <h3 id="result-title">{title}</h3>
        <p className="result-count">
          <strong>{emails_sent}</strong> of <strong>{emails_total}</strong> email
          {emails_total === 1 ? '' : 's'} sent
        </p>
        {emails_failed > 0 && (
          <p className="result-failed">
            {emails_failed} email{emails_failed === 1 ? '' : 's'} failed to send
          </p>
        )}
        <button ref={closeRef} type="button" className="result-close" onClick={onClose}>
          OK
        </button>
      </div>
    </div>
  )
}
