import { useMemo, useState } from 'react'
import type { InputMode } from '../../types/email'
import LoaderModal from '../LoaderModal'
import ResultModal from '../ResultModal'
import HomeHero from '../HomeHero'
import HomeAside, { type FormReadiness } from '../HomeAside'
import { useSendEmails } from './useSendEmails'
import '../HomePage.css'
import './EmailForm.css'

function countManualEmails(value: string): number {
  return value
    .split(/[,;\n]+/)
    .map((addr) => addr.trim())
    .filter(Boolean).length
}

export default function EmailForm() {
  const [subject, setSubject] = useState('')
  const [content, setContent] = useState('')
  const [banner, setBanner] = useState<File | null>(null)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [manualEmails, setManualEmails] = useState('')
  const [mode, setMode] = useState<InputMode>('file')
  const { loading, error, result, clearResult, clearError, submit } = useSendEmails()

  const readiness: FormReadiness = useMemo(
    () => ({
      hasSubject: subject.trim().length > 0,
      hasContent: content.trim().length > 0,
      hasBanner: Boolean(banner),
      hasRecipients:
        mode === 'file' ? Boolean(csvFile) : countManualEmails(manualEmails) > 0,
    }),
    [subject, content, banner, csvFile, mode, manualEmails],
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    await submit({ subject, content, banner, mode, csvFile, manualEmails })
  }

  return (
    <>
      <LoaderModal show={loading} />
      <ResultModal result={result} onClose={clearResult} />

      <div className="home-page">
        <HomeHero readiness={readiness} />

        <div className="home-layout">
          <form className="email-form" onSubmit={handleSubmit}>
            <header className="email-form-header">
              <h2>Compose campaign</h2>
              <p>Fill each section below. The checklist updates as you go.</p>
            </header>

            <section className="form-section" aria-labelledby="section-message">
              <h2 id="section-message">Message</h2>
              <div className="field">
                <label htmlFor="email-subject">Subject</label>
                <input
                  id="email-subject"
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Email subject line"
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="email-content">Content</label>
                <textarea
                  id="email-content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Write your email body. URLs become clickable buttons."
                  required
                />
              </div>
            </section>

            <section className="form-section" aria-labelledby="section-banner">
              <h2 id="section-banner">Banner</h2>
              <div className="field">
                <label htmlFor="email-banner">Banner image</label>
                <div className="file-field">
                  <input
                    id="email-banner"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setBanner(e.target.files?.[0] ?? null)}
                    required
                  />
                  {banner && <span className="file-name">{banner.name}</span>}
                </div>
              </div>
            </section>

            <section className="form-section" aria-labelledby="section-recipients">
              <h2 id="section-recipients">Recipients</h2>
              <fieldset className="mode-fieldset">
                <legend className="sr-only">Recipient input method</legend>
                <div className="mode-toggle" role="group" aria-label="Recipient input method">
                  <button
                    type="button"
                    className={`mode-option${mode === 'file' ? ' is-active' : ''}`}
                    aria-pressed={mode === 'file'}
                    onClick={() => setMode('file')}
                  >
                    Upload CSV / Excel
                  </button>
                  <button
                    type="button"
                    className={`mode-option${mode === 'manual' ? ' is-active' : ''}`}
                    aria-pressed={mode === 'manual'}
                    onClick={() => setMode('manual')}
                  >
                    Enter emails manually
                  </button>
                </div>
              </fieldset>

              {mode === 'file' ? (
                <div className="field">
                  <label htmlFor="email-csv">Recipient file</label>
                  <div className="file-field">
                    <input
                      id="email-csv"
                      type="file"
                      accept=".csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
                      onChange={(e) => setCsvFile(e.target.files?.[0] ?? null)}
                      required
                    />
                    {csvFile && <span className="file-name">{csvFile.name}</span>}
                  </div>
                  <p className="field-hint">File must include an Email column.</p>
                </div>
              ) : (
                <div className="field">
                  <label htmlFor="email-manual">Email addresses</label>
                  <textarea
                    id="email-manual"
                    value={manualEmails}
                    onChange={(e) => setManualEmails(e.target.value)}
                    placeholder="Comma, semicolon, or newline separated"
                    required
                  />
                  {countManualEmails(manualEmails) > 0 && (
                    <p className="field-hint">
                      {countManualEmails(manualEmails)} address
                      {countManualEmails(manualEmails) === 1 ? '' : 'es'} detected
                    </p>
                  )}
                </div>
              )}
            </section>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Sending…' : 'Send emails'}
            </button>

            {error && (
              <div className="form-alert form-alert-error" role="alert">
                {error}
              </div>
            )}
          </form>

          <HomeAside readiness={readiness} />
        </div>
      </div>
    </>
  )
}
