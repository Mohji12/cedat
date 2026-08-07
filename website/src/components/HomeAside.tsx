export type FormReadiness = {
  hasSubject: boolean
  hasContent: boolean
  hasBanner: boolean
  hasRecipients: boolean
}

type HomeAsideProps = {
  readiness: FormReadiness
}

const STEPS = [
  {
    title: 'Compose',
    detail: 'Add a clear subject and body. Paste a URL to turn it into a button.',
  },
  {
    title: 'Attach banner',
    detail: 'Upload a wide image (JPG/PNG). It appears at the top of every email.',
  },
  {
    title: 'Choose recipients',
    detail: 'Upload a CSV/Excel with an Email column, or paste addresses manually.',
  },
  {
    title: 'Send',
    detail: 'We deliver each message and show how many emails were sent.',
  },
]

const TIPS = [
  'CSV/Excel must include a column named Email or Email Address.',
  'Use a banner around 1200×400px for a sharp look on desktop and mobile.',
  'Keep subjects short — under 60 characters works best.',
  'One link in the body becomes a teal “Click Here” button automatically.',
]

export default function HomeAside({ readiness }: HomeAsideProps) {
  const checks = [
    { key: 'subject', label: 'Subject added', done: readiness.hasSubject },
    { key: 'content', label: 'Message written', done: readiness.hasContent },
    { key: 'banner', label: 'Banner attached', done: readiness.hasBanner },
    { key: 'recipients', label: 'Recipients ready', done: readiness.hasRecipients },
  ]
  const doneCount = checks.filter((c) => c.done).length
  const ready = doneCount === checks.length

  return (
    <aside className="home-aside" aria-label="Helpful guides">
      <section className="aside-panel aside-ready">
        <div className="aside-panel-head">
          <h2>Campaign checklist</h2>
          <span className={`ready-pill${ready ? ' is-ready' : ''}`}>
            {doneCount}/{checks.length}
          </span>
        </div>
        <div
          className="ready-bar"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={checks.length}
          aria-valuenow={doneCount}
          aria-label="Campaign readiness"
        >
          <span style={{ width: `${(doneCount / checks.length) * 100}%` }} />
        </div>
        <ul className="ready-list">
          {checks.map((item) => (
            <li key={item.key} className={item.done ? 'is-done' : undefined}>
              <span className="ready-mark" aria-hidden="true">
                {item.done ? '✓' : ''}
              </span>
              {item.label}
            </li>
          ))}
        </ul>
        <p className="aside-note">
          {ready
            ? 'Everything looks ready — hit Send emails when you are set.'
            : 'Complete each item to unlock a smoother send.'}
        </p>
      </section>

      <section className="aside-panel">
        <h2>How it works</h2>
        <ol className="how-list">
          {STEPS.map((step, index) => (
            <li key={step.title}>
              <span className="how-step">{index + 1}</span>
              <div>
                <strong>{step.title}</strong>
                <p>{step.detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="aside-panel">
        <h2>Quick tips</h2>
        <ul className="tips-list">
          {TIPS.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ul>
      </section>
    </aside>
  )
}
