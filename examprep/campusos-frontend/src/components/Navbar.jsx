import { NavLink } from 'react-router-dom'
import './Navbar.css'

const links = [
  { to: '/',          label: 'Home' },
  { to: '/flashcards', label: 'Flashcards' },
  { to: '/quiz',       label: 'Quiz' },
  { to: '/studyplan',  label: 'Study Plan' },
  { to: '/copilot',    label: 'Copilot' },
]

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-logo">
        <span className="logo-icon">⬡</span>
        <span className="logo-text">Campus<span className="logo-accent">OS</span></span>
      </NavLink>

      <ul className="navbar-links">
        {links.map(l => (
          <li key={l.to}>
            <NavLink to={l.to} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} end={l.to === '/'}>
              {l.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
