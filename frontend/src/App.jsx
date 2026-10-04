import { Link, Route, Routes, useParams } from 'react-router'
import HomePage from './pages/HomePage.jsx'
import TalkPage from './pages/TalkPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

function TalkRoute() {
  const { id } = useParams()
  if (!/^\d+$/.test(id)) return <NotFoundPage talk />

  // Each identity owns its request state, including during rapid navigation.
  return <TalkPage key={id} id={id} />
}

export default function App() {
  return (
    <>
      <header className="site-header"><Link to="/">PsychTalk Hub</Link></header>
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/events/:id" element={<TalkRoute />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <footer>Independent portfolio prototype. Not affiliated with Conn8cting.</footer>
    </>
  )
}
