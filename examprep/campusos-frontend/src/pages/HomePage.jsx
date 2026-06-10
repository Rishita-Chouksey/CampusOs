import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { checkHealth } from '../services/api'
import './HomePage.css'

const features = [
  {
    to: '/flashcards',
    icon: '🃏',
    title: 'Flashcards',
    desc: 'Paste your notes — get a deck of Q&A cards instantly. Flip through concepts until they stick.',
  },
  {
    to: '/quiz',
    icon: '📝',
    title: 'MCQ Quiz',
    desc: 'Test yourself with auto-generated multiple-choice questions. Pick difficulty, check answers.',
  },
  {
    to: '/studyplan',
    icon: '📅',
    title: 'Study Plan',
    desc: 'Tell it your subject and days left. Get a day-by-day revision roadmap built around your exam.',
  },
  {
    to: '/copilot',
    icon: '🤖',
    title: 'AI Copilot',
    desc: 'Just describe what you need in plain English. The copilot routes to the right tool automatically.',
  },
]

export default function HomePage() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    checkHealth()
      .then(r => setHealth({ ok: true, model: r.data.model }))
      .catch(() => setHealth({ ok: false }))
  }, [])

  return (
    <main className="home">
      {/* Hero */}
      <section className="hero">
        <div className="hero-bg-grid" aria-hidden />
        <div className="hero-inner">
          <div className="pill pill-violet hero-eyebrow">AI-Powered Exam Prep</div>
          <h1 className="hero-headline">
            Study smarter.<br />
            <span className="gradient-text">Stress less.</span>
          </h1>
          <p className="hero-sub">
            CampusOS turns your messy lecture notes into flashcards, quizzes, and study plans
            — powered by Gemini, built for engineers.
          </p>
          <div className="hero-ctas">
            <Link to="/copilot" className="btn btn-primary">Try AI Copilot</Link>
            <Link to="/flashcards" className="btn btn-ghost">Generate Flashcards</Link>
          </div>

          {health && (
            <div className={`status-badge ${health.ok ? 'ok' : 'err'}`}>
              <span className="status-dot" />
              {health.ok ? `API online · ${health.model}` : 'API offline — start the backend'}
            </div>
          )}
        </div>
      </section>

      {/* Feature Grid */}
      <section className="features-section">
        <div className="section-label">What it does</div>
        <div className="features-grid">
          {features.map(f => (
            <Link key={f.to} to={f.to} className="feature-card">
              <span className="feature-icon">{f.icon}</span>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
              <span className="feature-arrow">→</span>
            </Link>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="how-section">
        <div className="section-label">How it works</div>
        <div className="steps">
          {[
            ['Paste your notes', 'Drop in raw lecture text — no formatting needed.'],
            ['Pick a tool', 'Choose flashcards, quiz, study plan, or let the copilot decide.'],
            ['Study with focus', 'Get structured material back in seconds. Go learn.'],
          ].map(([title, desc], i) => (
            <div key={i} className="step">
              <span className="step-num">{String(i + 1).padStart(2, '0')}</span>
              <div>
                <h3>{title}</h3>
                <p>{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
