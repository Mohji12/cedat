import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  fetchAnalyticsSummary,
  fetchCampaignDetail,
  fetchCampaigns,
  fetchFailures,
  fetchVolume,
} from '../lib/api'
import type {
  AnalyticsSummary,
  CampaignDetail,
  CampaignListItem,
  FailureItem,
  VolumePoint,
} from '../types/email'
import './AnalyticsDashboard.css'

function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10)
}

function rangePreset(days: number): { from: string; to: string } {
  const to = new Date()
  const from = new Date()
  from.setDate(to.getDate() - (days - 1))
  return { from: isoDate(from), to: isoDate(to) }
}

function VolumeChart({ points }: { points: VolumePoint[] }) {
  const max = Math.max(1, ...points.map((p) => Math.max(p.attempted, p.delivered, p.failed)))
  if (!points.length) {
    return <p className="dash-empty">No volume data in this range.</p>
  }
  return (
    <div className="volume-chart" role="img" aria-label="Email volume by day">
      {points.map((p) => (
        <div key={p.day} className="volume-col">
          <div className="volume-bars">
            <span
              className="bar bar-attempted"
              style={{ height: `${(p.attempted / max) * 100}%` }}
              title={`Attempted ${p.attempted}`}
            />
            <span
              className="bar bar-delivered"
              style={{ height: `${(p.delivered / max) * 100}%` }}
              title={`Delivered ${p.delivered}`}
            />
            <span
              className="bar bar-failed"
              style={{ height: `${(p.failed / max) * 100}%` }}
              title={`Failed ${p.failed}`}
            />
          </div>
          <span className="volume-label">{p.day.slice(5)}</span>
        </div>
      ))}
    </div>
  )
}

export default function AnalyticsDashboard() {
  const initial = useMemo(() => rangePreset(30), [])
  const [preset, setPreset] = useState<7 | 30 | 90 | 'custom'>(30)
  const [from, setFrom] = useState(initial.from)
  const [to, setTo] = useState(initial.to)
  const [q, setQ] = useState('')
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [campaigns, setCampaigns] = useState<CampaignListItem[]>([])
  const [volume, setVolume] = useState<VolumePoint[]>([])
  const [failures, setFailures] = useState<FailureItem[]>([])
  const [detail, setDetail] = useState<CampaignDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const applyPreset = (days: 7 | 30 | 90) => {
    const range = rangePreset(days)
    setPreset(days)
    setFrom(range.from)
    setTo(range.to)
  }

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [s, c, v, f] = await Promise.all([
        fetchAnalyticsSummary({ from, to }),
        fetchCampaigns({ from, to, q: q.trim() || undefined, limit: 50 }),
        fetchVolume({ from, to }),
        fetchFailures({ from, to }),
      ])
      setSummary(s)
      setCampaigns(c.items)
      setVolume(v.items)
      setFailures(f.items)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics.')
    } finally {
      setLoading(false)
    }
  }, [from, to, q])

  useEffect(() => {
    void load()
  }, [load])

  const openDetail = async (id: string) => {
    try {
      const data = await fetchCampaignDetail(id)
      setDetail(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load campaign.')
    }
  }

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <div>
          <h1>Analytics</h1>
          <p>Delivery KPIs and campaign history from MySQL.</p>
        </div>
        <div className="analytics-filters">
          <div className="preset-group" role="group" aria-label="Date range">
            {([7, 30, 90] as const).map((d) => (
              <button
                key={d}
                type="button"
                className={`preset-btn${preset === d ? ' is-active' : ''}`}
                onClick={() => applyPreset(d)}
              >
                {d}d
              </button>
            ))}
            <button
              type="button"
              className={`preset-btn${preset === 'custom' ? ' is-active' : ''}`}
              onClick={() => setPreset('custom')}
            >
              Custom
            </button>
          </div>
          <label className="filter-field">
            From
            <input
              type="date"
              value={from}
              onChange={(e) => {
                setPreset('custom')
                setFrom(e.target.value)
              }}
            />
          </label>
          <label className="filter-field">
            To
            <input
              type="date"
              value={to}
              onChange={(e) => {
                setPreset('custom')
                setTo(e.target.value)
              }}
            />
          </label>
          <label className="filter-field filter-search">
            Search
            <input
              type="search"
              placeholder="Subject…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </label>
          <button type="button" className="refresh-btn" onClick={() => void load()} disabled={loading}>
            {loading ? 'Loading…' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && (
        <div className="dash-alert" role="alert">
          {error}
        </div>
      )}

      <section className="kpi-grid" aria-label="Key metrics">
        {[
          { label: 'Campaigns', value: summary?.campaigns ?? '—' },
          { label: 'Attempted', value: summary?.attempted ?? '—' },
          { label: 'Delivered', value: summary?.delivered ?? '—' },
          { label: 'Failed', value: summary?.failed ?? '—' },
          {
            label: 'Success rate',
            value: summary ? `${summary.success_rate}%` : '—',
          },
          {
            label: 'Avg / campaign',
            value: summary?.avg_recipients ?? '—',
          },
        ].map((kpi) => (
          <article key={kpi.label} className="kpi-card">
            <p>{kpi.label}</p>
            <strong>{kpi.value}</strong>
          </article>
        ))}
      </section>

      <div className="analytics-grid">
        <section className="dash-panel">
          <h2>Volume over time</h2>
          <div className="chart-legend">
            <span><i className="swatch attempted" /> Attempted</span>
            <span><i className="swatch delivered" /> Delivered</span>
            <span><i className="swatch failed" /> Failed</span>
          </div>
          <VolumeChart points={volume} />
        </section>

        <section className="dash-panel">
          <h2>Failure breakdown</h2>
          {failures.length === 0 ? (
            <p className="dash-empty">No failures in this range.</p>
          ) : (
            <ul className="failure-list">
              {failures.map((f) => (
                <li key={f.error_message}>
                  <span className="failure-count">{f.count}</span>
                  <span className="failure-msg">{f.error_message}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <section className="dash-panel">
        <h2>Campaign history</h2>
        {campaigns.length === 0 ? (
          <p className="dash-empty">No campaigns found.</p>
        ) : (
          <div className="table-wrap">
            <table className="campaign-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Subject</th>
                  <th>Total</th>
                  <th>Sent</th>
                  <th>Failed</th>
                  <th>Success %</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((c) => (
                  <tr key={c.id} onClick={() => void openDetail(c.id)}>
                    <td>{c.created_at ?? '—'}</td>
                    <td>{c.subject}</td>
                    <td>{c.emails_total}</td>
                    <td>{c.emails_sent}</td>
                    <td>{c.emails_failed}</td>
                    <td>{c.success_rate}%</td>
                    <td>
                      <span className={`status-pill status-${c.status}`}>{c.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {detail && (
        <div
          className="detail-backdrop"
          role="dialog"
          aria-modal="true"
          aria-labelledby="detail-title"
          onClick={(e) => {
            if (e.target === e.currentTarget) setDetail(null)
          }}
        >
          <div className="detail-modal">
            <header>
              <h3 id="detail-title">{detail.subject}</h3>
              <button type="button" onClick={() => setDetail(null)} aria-label="Close">
                ×
              </button>
            </header>
            <p className="detail-meta">
              {detail.created_at} · {detail.emails_sent}/{detail.emails_total} sent ·{' '}
              <span className={`status-pill status-${detail.status}`}>{detail.status}</span>
            </p>
            <div className="table-wrap">
              <table className="campaign-table">
                <thead>
                  <tr>
                    <th>Recipient</th>
                    <th>Status</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.events.map((ev, i) => (
                    <tr key={`${ev.recipient_email}-${i}`}>
                      <td>{ev.recipient_email}</td>
                      <td>
                        <span className={`status-pill status-${ev.status === 'sent' ? 'success' : 'failed'}`}>
                          {ev.status}
                        </span>
                      </td>
                      <td>{ev.error_message || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
