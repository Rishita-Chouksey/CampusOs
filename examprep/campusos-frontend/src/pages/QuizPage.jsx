import { useState } from 'react'
import { genQuiz } from '../services/api'
import './ToolPage.css'
import './QuizPage.css'

export default function QuizPage() {
  const [notes, setNotes]     = useState('')
  const [num, setNum]         = useState(5)
  const [questions, setQ]     = useState([])
  const [answers, setAnswers] = useState({})
  const [submitted, setSubmit]= useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const generate = async () => {
    if (!notes.trim()) return
    setLoading(true); setError(''); setQ([]); setAnswers({}); setSubmit(false)
    try {
      const res = await genQuiz(notes, num)
      setQ(res.data.quiz)
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const score = submitted
    ? questions.filter((q, i) => answers[i] === q.answer).length
    : 0

  const reset = () => { setAnswers({}); setSubmit(false) }

  return (
    <main className="tool-page">
      <div className="tool-header">
        <div className="pill pill-violet">Quiz</div>
        <h2>MCQ Quiz Generator</h2>
        <p>Test yourself with auto-generated multiple-choice questions.</p>
      </div>

      <div className="tool-body">
        <div className="input-panel card">
          <label htmlFor="quiz-notes">Your notes</label>
          <textarea
            id="quiz-notes" rows={7}
            placeholder="Paste the content you want to be quizzed on…"
            value={notes} onChange={e => setNotes(e.target.value)}
          />
          <div className="quiz-controls">
            <div className="num-control">
              <label htmlFor="num-q">Questions</label>
              <input
                id="num-q" type="number" min={1} max={20}
                value={num} onChange={e => setNum(Number(e.target.value))}
                style={{width:80}}
              />
            </div>
            <button className="btn btn-primary" onClick={generate} disabled={loading || notes.trim().length < 10}>
              {loading ? <><span className="spinner" /> Generating…</> : '⚡ Generate Quiz'}
            </button>
          </div>
          {error && <div className="error-box">{error}</div>}
        </div>

        {questions.length > 0 && (
          <div className="quiz-section">
            {submitted && (
              <div className="score-banner">
                <span className="score-num">{score} / {questions.length}</span>
                <span className="score-label">correct</span>
                <button className="btn btn-ghost btn-sm" onClick={reset}>Retry</button>
              </div>
            )}

            <div className="quiz-list">
              {questions.map((q, i) => {
                const chosen = answers[i]
                const isRight = submitted && chosen === q.answer
                const isWrong = submitted && chosen && chosen !== q.answer
                return (
                  <div key={i} className={`quiz-item card ${isRight?'correct':''} ${isWrong?'wrong':''}`}>
                    <p className="quiz-q"><span className="q-num">Q{i+1}</span> {q.question}</p>
                    <div className="options">
                      {q.options.map((opt, j) => {
                        const letter = ['A','B','C','D'][j]
                        const isSel = chosen === letter
                        const isCorrectOpt = submitted && letter === q.answer
                        return (
                          <button
                            key={j}
                            disabled={submitted}
                            className={`option-btn
                              ${isSel ? 'selected' : ''}
                              ${isCorrectOpt ? 'correct-opt' : ''}
                              ${submitted && isSel && !isCorrectOpt ? 'wrong-opt' : ''}
                            `}
                            onClick={() => !submitted && setAnswers(a => ({...a, [i]: letter}))}
                          >
                            <span className="opt-letter">{letter}</span>
                            {opt.replace(/^[A-D]\.\s*/, '')}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>

            {!submitted && (
              <button
                className="btn btn-primary"
                style={{marginTop:8}}
                disabled={Object.keys(answers).length < questions.length}
                onClick={() => setSubmit(true)}
              >
                Submit Answers
              </button>
            )}
          </div>
        )}

        {!loading && questions.length === 0 && notes.length === 0 && (
          <div className="empty-state">
            <div className="icon">📝</div>
            <p>Your quiz will appear here.</p>
          </div>
        )}
      </div>
    </main>
  )
}
