import { useState } from 'react'
import { genStudyPlan } from '../services/api'
import './ToolPage.css'
import './StudyPlanPage.css'

export default function StudyPlanPage() {
  const [subject, setSubject] = useState('')
  const [days, setDays]       = useState(7)
  const [plan, setPlan]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const generate = async () => {
    if (!subject.trim()) return
    setLoading(true); setError(''); setPlan(null)
    try {
      const res = await genStudyPlan(subject, days)
      setPlan(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const entries = plan ? Object.entries(plan.study_plan) : []

  return (
    <main className="tool-page">
      <div className="tool-header">
        <div className="pill pill-violet">Study Plan</div>
        <h2>Day-wise Study Plan</h2>
        <p>Enter your subject and exam countdown — get a structured revision roadmap.</p>
      </div>

      <div className="tool-body">
        <div className="input-panel card">
          <div className="plan-inputs">
            <div style={{flex:1}}>
              <label htmlFor="subject">Subject</label>
              <input
                id="subject" type="text"
                placeholder="e.g. Computer Networks, DBMS, Thermodynamics…"
                value={subject} onChange={e => setSubject(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && generate()}
              />
            </div>
            <div>
              <label htmlFor="days">Days left</label>
              <input
                id="days" type="number" min={1} max={60}
                value={days} onChange={e => setDays(Number(e.target.value))}
                style={{width:90}}
              />
            </div>
          </div>
          <div className="input-footer">
            <span />
            <button className="btn btn-primary" onClick={generate} disabled={loading || !subject.trim()}>
              {loading ? <><span className="spinner" /> Generating…</> : '📅 Build My Plan'}
            </button>
          </div>
          {error && <div className="error-box">{error}</div>}
        </div>

        {plan && (
          <div className="plan-section">
            <div className="plan-meta">
              <span className="pill pill-green">{entries.length} days</span>
              <span className="plan-title-txt">{plan.subject}</span>
            </div>
            <div className="plan-timeline">
              {entries.map(([day, text], i) => {
                const isLast = i === entries.length - 1
                return (
                  <div key={day} className={`plan-day ${isLast ? 'final-day' : ''}`}>
                    <div className="day-marker">
                      <span className="day-dot" />
                      {i < entries.length - 1 && <span className="day-line" />}
                    </div>
                    <div className="day-content card">
                      <span className="day-label">{day}{isLast ? ' · Revision' : ''}</span>
                      <p>{text}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {!loading && !plan && (
          <div className="empty-state">
            <div className="icon">📅</div>
            <p>Your study plan will appear here.</p>
          </div>
        )}
      </div>
    </main>
  )
}
