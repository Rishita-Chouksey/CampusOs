import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE })

export const checkHealth   = ()       => api.get('/health')
export const genFlashcards = (notes)  => api.post('/flashcards', { notes_text: notes })
export const genQuiz       = (notes, num) => api.post('/quiz', { notes_text: notes, num_questions: num })
export const genStudyPlan  = (subject, days) => api.post('/studyplan', { subject, days_left: days })
export const askCopilot    = (payload) => api.post('/copilot', payload)
