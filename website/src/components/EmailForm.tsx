import { useState } from 'react'
import { sendEmails } from '../lib/api'
import './EmailForm.css'

function LoaderModal({ show }: { show: boolean }) {
  if (!show) return null
  return (
    <div className="modal-backdrop">
      <div className="modal-loader">
        <div className="spinner" />
        <div>Sending emails, please wait...</div>
      </div>
    </div>
  )
}

type InputMode = 'file' | 'manual'

export default function EmailForm() {
  const [subject, setSubject] = useState('')
  const [content, setContent] = useState('')
  const [banner, setBanner] = useState<File | null>(null)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [manualEmails, setManualEmails] = useState('')
  const [mode, setMode] = useState<InputMode>('file')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    const formData = new FormData()
    formData.append('subject', subject)
    formData.append('content', content)
    if (banner) formData.append('banner', banner)
    if (mode === 'file' && csvFile) {
      formData.append('csv_file', csvFile)
    } else if (mode === 'manual') {
      const emails = manualEmails
        .split(/[,;\n]+/)
        .map((addr) => addr.trim())
        .filter(Boolean)
      const csvContent = 'email\n' + emails.join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv' })
      formData.append('csv_file', blob, 'manual_emails.csv')
    }
    try {
      const response = await sendEmails(formData)
      const data = (await response.json()) as { message?: string }
      setMessage(data.message ?? 'Emails sent successfully!')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error sending emails. Please try again.'
      setMessage(msg)
      console.error('Error sending emails:', err)
    }
    setLoading(false)
  }

  return (
    <>
      <LoaderModal show={loading} />
      <form className="email-form" onSubmit={handleSubmit}>
        <h2>Send Bulk Email</h2>
        <div>
          <label htmlFor="email-subject">Subject:</label>
          <input
            id="email-subject"
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="email-content">Content:</label>
          <textarea
            id="email-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="email-banner">Banner Image:</label>
          <input
            id="email-banner"
            type="file"
            accept="image/*"
            onChange={(e) => setBanner(e.target.files?.[0] ?? null)}
            required
          />
        </div>
        <div>
          <label>Choose Email Input Method:</label>
          <div className="radio-group">
            <label>
              <input
                type="radio"
                name="mode"
                value="file"
                checked={mode === 'file'}
                onChange={() => setMode('file')}
              />
              Upload CSV/Excel
            </label>
            <label style={{ marginLeft: '1em' }}>
              <input
                type="radio"
                name="mode"
                value="manual"
                checked={mode === 'manual'}
                onChange={() => setMode('manual')}
              />
              Enter Emails Manually
            </label>
          </div>
        </div>
        {mode === 'file' ? (
          <div>
            <label htmlFor="email-csv">CSV/Excel File:</label>
            <input
              id="email-csv"
              type="file"
              accept=".csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
              onChange={(e) => setCsvFile(e.target.files?.[0] ?? null)}
              required
            />
          </div>
        ) : (
          <div>
            <label htmlFor="email-manual">Emails (comma, semicolon, or newline separated):</label>
            <textarea
              id="email-manual"
              value={manualEmails}
              onChange={(e) => setManualEmails(e.target.value)}
              required
            />
          </div>
        )}
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Emails'}
        </button>
        {message && <div className="form-message">{message}</div>}
      </form>
    </>
  )
}
