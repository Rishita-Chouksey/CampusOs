import { useState, useRef, useEffect } from 'react'
import { askCopilot } from '../services/api'
import './ToolPage.css'
import './CopilotPage.css'

const SUGGESTIONS = [
  'Generate flashcards from my notes',
  'Create a quiz from my notes',
  'Make a study plan for Computer Networks in 5 days',
  'Build a study plan for DBMS exam in 3 days',
]

function renderResult(intent, result) {
  if (!result) return null

  if (intent === 'flashcard' && Array.isArray(result)) {
    return (
      <div className="copilot-result">
        <div className="res-label">Flashcards · {result.length}</div>
        <div className="cop-cards">
          {result.map((c, i) => (
            <div key={i} className="cop-card">
              <span className="cop-q">{c.question}</span>
              <span className="cop-a">{c.answer}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (intent === 'quiz' && Array.isArray(result)) {
    return (
      <div className="copilot-result">
        <div className="res-label">Quiz · {result.length} questions</div>
        {result.map((q, i) => (
          <div key={i} className="cop-q-item">
            <p><strong>Q{i+1}.</strong> {q.question}</p>
            <ul>
              {q.options.map((o, j) => (
                <li key={j} className={['A','B','C','D'][j] === q.answer ? 'correct-li' : ''}>{o}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    )
  }

  if (intent === 'study_plan' && typeof result === 'object') {
    return (
      <div className="copilot-result">
        <div className="res-label">Study Plan</div>
        {Object.entries(result).map(([day, text]) => (
          <div key={day} className="cop-day">
            <span className="cop-day-lbl">{day}</span>
            <p>{text}</p>
          </div>
        ))}
      </div>
    )
  }

  return null
}

export default function CopilotPage() {
  const [messages, setMessages] = useState([])
  const [query, setQuery]       = useState('')
  const [notes, setNotes]       = useState('')
  const [subject, setSubject]   = useState('')
  const [days, setDays]         = useState(7)
  const [loading, setLoading]   = useState(false)
  const [showCtx, setShowCtx]   = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (overrideQuery) => {
    const q = (overrideQuery || query).trim()
    if (!q) return

    const userMsg = { role: 'user', text: q }
    setMessages(m => [...m, userMsg])
    setQuery(''); setLoading(true)

    try {
      const res = await askCopilot({
        query: q,
        notes_text: notes,
        subject,
        days_left: days,
      })
      const { intent, message, response: result } = res.data
      setMessages(m => [...m, { role: 'assistant', intent, text: message, result }])
    } catch (e) {
      const err = e.response?.data?.detail || 'API error — is the backend running?'
      setMessages(m => [...m, { role: 'assistant', intent: 'error', text: err, result: null }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="tool-page">
      <div className="tool-header">
        <div className="pill pill-violet">Copilot</div>
        <h2>AI Copilot</h2>
        <p>Describe what you need in plain English — the copilot routes to the right tool.</p>
      </div>

      <div className="tool-body">
        {/* Context panel (collapsible) */}
        <div className="card ctx-panel">
          <button className="ctx-toggle" onClick={() => setShowCtx(s => !s)}>
            <span>⚙ Context (notes / subject)</span>
            <span className="ctx-arrow">{showCtx ? '▲' : '▼'}</span>
          </button>
          {showCtx && (
            <div className="ctx-body">
              <label>Notes (for flashcard / quiz intents)</label>
              <textarea rows={5} placeholder="Paste study notes here…" value={notes} onChange={e => setNotes(e.target.value)} />
              <div className="ctx-row">
                <div style={{flex:1}}>
                  <label>Subject (for study plan)</label>
                  <input type="text" placeholder="e.g. Computer Networks" value={subject} onChange={e => setSubject(e.target.value)} />
                </div>
                <div>
                  <label>Days left</label>
                  <input type="number" min={1} max={60} value={days} onChange={e => setDays(Number(e.target.value))} style={{width:80}} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Chat window */}
        <div className="chat-window card">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <span className="chat-empty-icon">🤖</span>
              <p>Ask me anything about your exam prep.</p>
              <div className="suggestions">
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} className="suggestion-btn" onClick={() => send(s)}>{s}</button>
                ))}
              </div>
            </div>
          ) : (
            <div className="chat-messages">
              {messages.map((m, i) => (
                <div key={i} className={`chat-msg ${m.role}`}>
                  <span className="msg-avatar">{m.role === 'user' ? '👤' : '🤖'}</span>
                  <div className="msg-body">
                    <p className="msg-text">{m.text}</p>
                    {m.role === 'assistant' && renderResult(m.intent, m.result)}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="chat-msg assistant">
                  <span className="msg-avatar">🤖</span>
                  <div className="msg-body typing">
                    <span /><span /><span />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input row */}
        <div className="chat-input-row card">
          <textarea
            rows={2} placeholder="e.g. 'Generate flashcards from my notes' or 'Study plan for Algorithms in 4 days'…"
            value={query} onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
          />
          <button className="btn btn-primary" onClick={() => send()} disabled={loading || !query.trim()}>
            {loading ? <span className="spinner" /> : '↑ Send'}
          </button>
        </div>
      </div>
    </main>
  )
}
