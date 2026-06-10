import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import FlashcardsPage from './pages/FlashcardsPage'
import QuizPage from './pages/QuizPage'
import StudyPlanPage from './pages/StudyPlanPage'
import CopilotPage from './pages/CopilotPage'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"           element={<HomePage />} />
        <Route path="/flashcards" element={<FlashcardsPage />} />
        <Route path="/quiz"       element={<QuizPage />} />
        <Route path="/studyplan"  element={<StudyPlanPage />} />
        <Route path="/copilot"    element={<CopilotPage />} />
      </Routes>
    </BrowserRouter>
  )
}
