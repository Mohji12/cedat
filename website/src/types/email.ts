export type InputMode = 'file' | 'manual'

export type SendResult = {
  emails_sent: number
  emails_failed: number
  emails_total: number
}

export type SendEmailsResponse = {
  message?: string
  emails_sent?: number
  emails_failed?: number
  emails_total?: number
  rows_stored?: number
  columns_stored?: string[]
  files_stored?: Array<Record<string, string>>
  list_stored_at?: string
  list_public_id?: string | null
  campaign_id?: string | null
  error?: string
}

export type AnalyticsSummary = {
  campaigns: number
  attempted: number
  delivered: number
  failed: number
  success_rate: number
  avg_recipients: number
}

export type CampaignListItem = {
  id: string
  created_at: string | null
  subject: string
  content_preview?: string | null
  banner_url?: string | null
  emails_total: number
  emails_sent: number
  emails_failed: number
  success_rate: number
  status: string
  list_public_id?: string | null
  list_folder?: string | null
  source?: string
}

export type CampaignDetail = CampaignListItem & {
  events: Array<{
    recipient_email: string
    status: string
    error_message?: string | null
    provider_response_id?: string | null
    created_at?: string | null
  }>
}

export type VolumePoint = {
  day: string
  attempted: number
  delivered: number
  failed: number
}

export type FailureItem = {
  error_message: string
  count: number
}

export type DateRangeParams = {
  from?: string
  to?: string
  q?: string
}
