import type { FormReadiness } from './HomeAside'
import './HomePage.css'

type HomeHeroProps = {
  readiness: FormReadiness
}

export default function HomeHero({ readiness }: HomeHeroProps) {
  const done = [
    readiness.hasSubject,
    readiness.hasContent,
    readiness.hasBanner,
    readiness.hasRecipients,
  ].filter(Boolean).length

  return (
    <section className="home-hero" aria-labelledby="home-hero-title">
      <div className="home-hero-copy">
        <p className="home-hero-eyebrow">CEDAT outreach</p>
        <h1 id="home-hero-title">Send polished bulk emails in minutes</h1>
        <p className="home-hero-lead">
          Write once, attach your banner, add recipients, and deliver — with a clear
          send summary when you are done.
        </p>
      </div>
      <ul className="home-hero-stats" aria-label="Campaign highlights">
        <li>
          <strong>{done}/4</strong>
          <span>Steps complete</span>
        </li>
        <li>
          <strong>CSV</strong>
          <span>or paste emails</span>
        </li>
        <li>
          <strong>Banner</strong>
          <span>on every mail</span>
        </li>
      </ul>
    </section>
  )
}
