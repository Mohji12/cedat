import type {
  AnalyticsSummary,
  CampaignDetail,
  CampaignListItem,
  FailureItem,
  SendEmailsResponse,
  VolumePoint,
} from '../types/email'

const DEFAULT_API_BASE = 'https://cedat.menteetracker.com'

function apiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined
  const trimmed = (raw ?? '').trim().replace(/\/$/, '')
  return trimmed || DEFAULT_API_BASE
}

async function parseJson<T>(response: Response): Promise<T> {
  try {
    return (await response.json()) as T
  } catch {
    return {} as T
  }
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`)
  const data = await parseJson<T & { error?: string }>(response)
  if (!response.ok) {
    throw new Error(data.error || `Server error: ${response.status} ${response.statusText}`)
  }
  return data
}

function withQuery(path: string, params: Record<string, string | number | undefined>): string {
  const qs = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') qs.set(key, String(value))
  }
  const query = qs.toString()
  return query ? `${path}?${query}` : path
}

export async function sendEmails(formData: FormData): Promise<SendEmailsResponse> {
  try {
    const response = await fetch(`${apiBaseUrl()}/send-emails`, {
      method: 'POST',
      body: formData,
    })

    const data = await parseJson<SendEmailsResponse>(response)

    if (!response.ok) {
      throw new Error(
        data.error || `Server error: ${response.status} ${response.statusText}`,
      )
    }

    return data
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

export async function fetchAnalyticsSummary(params: {
  from?: string
  to?: string
}): Promise<AnalyticsSummary> {
  return getJson(
    withQuery('/analytics/summary', { from: params.from, to: params.to }),
  )
}

export async function fetchCampaigns(params: {
  from?: string
  to?: string
  q?: string
  limit?: number
  offset?: number
}): Promise<{ total: number; items: CampaignListItem[] }> {
  return getJson(
    withQuery('/analytics/campaigns', {
      from: params.from,
      to: params.to,
      q: params.q,
      limit: params.limit,
      offset: params.offset,
    }),
  )
}

export async function fetchCampaignDetail(id: string): Promise<CampaignDetail> {
  return getJson(`/analytics/campaigns/${encodeURIComponent(id)}`)
}

export async function fetchVolume(params: {
  from?: string
  to?: string
}): Promise<{ items: VolumePoint[] }> {
  return getJson(withQuery('/analytics/volume', { from: params.from, to: params.to }))
}

export async function fetchFailures(params: {
  from?: string
  to?: string
}): Promise<{ items: FailureItem[] }> {
  return getJson(withQuery('/analytics/failures', { from: params.from, to: params.to }))
}
