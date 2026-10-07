import { useState } from 'react'
import { readTalks } from '../api/client.js'
import RequestState from '../components/RequestState.jsx'
import TalkCard from '../components/TalkCard.jsx'
import useApiRequest from '../hooks/useApiRequest.js'
import { groupTalks } from '../utils/talks.js'

function TalkGroup({ id, title, talks, emptyMessage }) {
  return (
    <section className="talk-group" aria-labelledby={id}>
      <h2 id={id}>{title}</h2>
      {talks.length === 0 ? <p>{emptyMessage}</p> : (
        <ul className="talk-grid">
          {talks.map((talk) => <li key={talk.id}><TalkCard talk={talk} /></li>)}
        </ul>
      )}
    </section>
  )
}

function TalkGroups({ talks }) {
  // One snapshot when a successful list mounts; refresh/navigation re-evaluates it.
  const [now] = useState(() => Date.now())
  const { upcoming, past } = groupTalks(talks, now)

  return (
    <>
      {talks.length === 0 && <p>Talks will appear here when they are added.</p>}
      <TalkGroup id="upcoming-title" title="Upcoming talks" talks={upcoming}
        emptyMessage="No upcoming talks yet. Explore past talks below." />
      <TalkGroup id="past-title" title="Past talks" talks={past}
        emptyMessage="No past talks yet." />
    </>
  )
}

export default function HomePage() {
  const { status, data: talks, retry } = useApiRequest(readTalks)

  return (
    <section aria-labelledby="home-title">
      <header className="home-intro">
        <p className="intro-eyebrow">Psychology · Ideas · Conversation</p>
        <h1 id="home-title">Keep learning<br />beyond the talk.</h1>
        <p className="intro-description">Big questions, fresh perspectives, and something good to read.
          Explore the ideas behind upcoming and past psychology talks.</p>
        <a className="intro-link" href="#upcoming-title">Find your next curiosity <span aria-hidden="true">↘</span></a>
      </header>
      <RequestState status={status} context="home" onRetry={retry} />
      {status === 'success' && <TalkGroups talks={talks} />}
    </section>
  )
}
