const DEFAULT_API_BASE =
  'https://nxvkvdws672xre7dwuxhajx67u0mplyd.lambda-url.ap-south-1.on.aws'

function apiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined
  const trimmed = (raw ?? '').trim().replace(/\/$/, '')
  return trimmed || DEFAULT_API_BASE
}

export async function sendEmails(formData: FormData): Promise<Response> {
  const base = apiBaseUrl()
  try {
    const response = await fetch(`${base}/send-emails`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      let errorMessage = `Server error: ${response.status} ${response.statusText}`
      try {
        const errorData = (await response.json()) as { error?: string }
        errorMessage = errorData.error ?? errorMessage
      } catch {
        const text = await response.text()
        errorMessage = text || errorMessage
      }
      throw new Error(errorMessage)
    }

    return response
  } catch (error: unknown) {
    if (
      error instanceof TypeError &&
      typeof error.message === 'string' &&
      error.message.includes('fetch')
    ) {
      throw new Error(
        'Network error: Unable to connect to the server. Please make sure the backend is running.',
      )
    }
    throw error
  }
}
