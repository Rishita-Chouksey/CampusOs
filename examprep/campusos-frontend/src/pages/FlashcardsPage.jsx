import { useState } from 'react'
import { genFlashcards } from '../services/api'
import './ToolPage.css'
import './FlashcardsPage.css'

export default function FlashcardsPage() {
  const [notes, setNotes]       = useState('')
  const [cards, setCards]       = useState([])
  const [flipped, setFlipped]   = useState({})
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [current, setCurrent]   = useState(0)
  const [view, setView]         = useState('grid') // 'grid' | 'focus'

  const generate = async () => {
    if (!notes.trim()) return
    setLoading(true); setError(''); setCards([]); setFlipped({})
    try {
      const res = await genFlashcards(notes)
      setCards(res.data.flashcards)
      setCurrent(0)
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const toggle = (i) => setFlipped(f => ({ ...f, [i]: !f[i] }))

  const prev = () => setCurrent(c => Math.max(0, c - 1))
  const next = () => setCurrent(c => Math.min(cards.length - 1, c + 1))

  return (
    <main className="tool-page">
      <div className="tool-header">
        <div className="pill pill-violet">Flashcards</div>
        <h2>Generate Flashcards</h2>
        <p>Paste any study notes — get back a ready-to-use Q&amp;A deck.</p>
      </div>

      <div className="tool-body">
        {/* Input panel */}
        <div className="input-panel card">
          <label htmlFor="notes">Your notes</label>
          <textarea
            id="notes" rows={8}
            placeholder="Paste lecture notes, textbook excerpts, or any study material here…"
            value={notes} onChange={e => setNotes(e.target.value)}
          />
          <div className="input-footer">
            <span className="char-count">{notes.length} chars</span>
            <button className="btn btn-primary" onClick={generate} disabled={loading || notes.trim().length < 10}>
              {loading ? <><span className="spinner" /> Generating…</> : '⚡ Generate Flashcards'}
            </button>
          </div>
          {error && <div className="error-box" style={{marginTop:12}}>{error}</div>}
        </div>

        {/* Results */}
        {cards.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <span className="pill pill-green">{cards.length} cards</span>
              <div className="view-toggle">
                <button className={`btn btn-sm btn-ghost ${view==='grid'?'active':''}`} onClick={()=>setView('grid')}>Grid</button>
                <button className={`btn btn-sm btn-ghost ${view==='focus'?'active':''}`} onClick={()=>setView('focus')}>Focus</button>
              </div>
            </div>

            {view === 'grid' ? (
              <div className="cards-grid">
                {cards.map((c, i) => (
                  <div
                    key={i}
                    className={`flip-card ${flipped[i] ? 'flipped' : ''}`}
                    onClick={() => toggle(i)}
                  >
                    <div className="flip-inner">
                      <div className="flip-front">
                        <span className="card-label">Question</span>
                        <p>{c.question}</p>
                        <span className="tap-hint">tap to reveal</span>
                      </div>
                      <div className="flip-back">
                        <span className="card-label answer">Answer</span>
                        <p>{c.answer}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="focus-mode">
                <div className={`flip-card focus-card ${flipped[current] ? 'flipped' : ''}`} onClick={() => toggle(current)}>
                  <div className="flip-inner">
                    <div className="flip-front">
                      <span className="card-label">Question</span>
                      <p>{cards[current].question}</p>
                      <span className="tap-hint">tap to reveal</span>
                    </div>
                    <div className="flip-back">
                      <span className="card-label answer">Answer</span>
                      <p>{cards[current].answer}</p>
                    </div>
                  </div>
                </div>
                <div className="focus-nav">
                  <button className="btn btn-ghost btn-sm" onClick={prev} disabled={current===0}>← Prev</button>
                  <span className="focus-counter">{current + 1} / {cards.length}</span>
                  <button className="btn btn-ghost btn-sm" onClick={next} disabled={current===cards.length-1}>Next →</button>
                </div>
              </div>
            )}
          </div>
        )}

        {!loading && cards.length === 0 && notes.length === 0 && (
          <div className="empty-state">
            <div className="icon">🃏</div>
            <p>Your flashcards will appear here.</p>
          </div>
        )}
      </div>
    </main>
  )
}
