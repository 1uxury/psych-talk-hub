import { useState } from 'react'
import { Link } from 'react-router'
import { readTalk } from '../api/client.js'
import RequestState from '../components/RequestState.jsx'
import ResourceCard from '../components/ResourceCard.jsx'
import useApiRequest from '../hooks/useApiRequest.js'
import { formatTalkTime, getTalkStatus } from '../utils/talks.js'

function TalkDetails({ talk }) {
  // Refresh, navigation or a successful retry mounts a new snapshot; no live timer.
  const [now] = useState(() => Date.now())

  return (
    <>
      <header className="talk-details">
        <div className="talk-labels">
          {talk.is_example && <p className="example-label">Example event</p>}
          <p className="talk-status">{getTalkStatus(talk.starts_at, now)}</p>
        </div>
        <h1 id="talk-title">{talk.title}</h1>
        {talk.topic && <p className="talk-topic">{talk.topic}</p>}
        <p className="talk-time">
          <time dateTime={talk.starts_at}>{formatTalkTime(talk.starts_at)}</time>
        </p>
        {talk.speaker && <p className="talk-speaker">Speaker: {talk.speaker}</p>}
        {talk.description && <p className="reading-text talk-description">{talk.description}</p>}
        {talk.is_example && (
          <p className="example-disclosure">
            Reading selections are illustrative; these talks are fictional.
          </p>
        )}
      </header>
      <section className="reading-section" aria-labelledby="reading-title">
        <h2 id="reading-title">Related reading</h2>
        <p>{talk.resource_count} reading {talk.resource_count === 1 ? 'resource' : 'resources'}</p>
        {talk.resources.length === 0 ? (
          <p>Reading resources will be added here soon.</p>
        ) : (
          <ul className="resource-list">
            {talk.resources.map((reading) => (
              <li key={reading.association_id}><ResourceCard reading={reading} /></li>
            ))}
          </ul>
        )}
      </section>
    </>
  )
}

export default function TalkPage({ id }) {
  const { status, data: talk, retry } = useApiRequest(readTalk, id)

  return (
    <section aria-labelledby="talk-title">
      <Link to="/">Back to talks</Link>
      {status === 'success' ? <TalkDetails talk={talk} /> : (
        <>
          <h1 id="talk-title">Talk</h1>
          <RequestState status={status} context="talk" onRetry={retry} />
        </>
      )}
    </section>
  )
}
