import { useCallback, useState } from 'react'
import { sendEmails } from '../../lib/api'
import type { InputMode, SendResult } from '../../types/email'

type UseSendEmailsReturn = {
  loading: boolean
  error: string | null
  result: SendResult | null
  clearResult: () => void
  clearError: () => void
  submit: (args: {
    subject: string
    content: string
    banner: File | null
    mode: InputMode
    csvFile: File | null
    manualEmails: string
  }) => Promise<void>
}

export function useSendEmails(): UseSendEmailsReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SendResult | null>(null)

  const clearResult = useCallback(() => setResult(null), [])
  const clearError = useCallback(() => setError(null), [])

  const submit = useCallback(
    async ({
      subject,
      content,
      banner,
      mode,
      csvFile,
      manualEmails,
    }: {
      subject: string
      content: string
      banner: File | null
      mode: InputMode
      csvFile: File | null
      manualEmails: string
    }) => {
      setLoading(true)
      setError(null)
      setResult(null)

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
        const data = await sendEmails(formData)
        const emails_sent = data.emails_sent ?? 0
        const emails_failed = data.emails_failed ?? 0
        const emails_total = data.emails_total ?? emails_sent + emails_failed
        setResult({ emails_sent, emails_failed, emails_total })
      } catch (err: unknown) {
        const msg =
          err instanceof Error ? err.message : 'Error sending emails. Please try again.'
        setError(msg)
        console.error('Error sending emails:', err)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  return { loading, error, result, clearResult, clearError, submit }
}
