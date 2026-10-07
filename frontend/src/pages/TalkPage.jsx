import { useRef, useState } from 'react'
import { Link } from 'react-router'
import { readTalk } from '../api/client.js'
import RequestState from '../components/RequestState.jsx'
import ResourceCard from '../components/ResourceCard.jsx'
import useApiRequest from '../hooks/useApiRequest.js'
import { formatTalkTime, getTalkStatus } from '../utils/talks.js'

function TalkDetails({ talk }) {
  // Refresh, navigation or a successful retry mounts a new snapshot; no live timer.
  const [now] = useState(() => Date.now())
  const [query, setQuery] = useState('')
  const searchInput = useRef(null)
  const search = query.trim().toLowerCase()
  const readings = talk.resources.filter((reading) => reading.title.toLowerCase().includes(search))

  function clearSearch() {
    setQuery('')
    searchInput.current?.focus()
  }

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
        {talk.resources.length > 0 && (
          <div className="resource-search">
            <label htmlFor="resource-search">Search resources</label>
            <input
              id="resource-search"
              ref={searchInput}
              type="search"
              placeholder="Search by title"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-describedby="reading-count"
              aria-controls="reading-results"
            />
          </div>
        )}
        <p id="reading-count" role="status" aria-atomic="true">
          {search ? `${readings.length} of ${talk.resource_count}` : talk.resource_count}
          {' '}reading {talk.resource_count === 1 ? 'resource' : 'resources'}
        </p>
        <div id="reading-results">
          {talk.resources.length === 0 ? (
            <p>Reading resources will be added here soon.</p>
          ) : readings.length === 0 ? (
            <div>
              <p>No resources match your search.</p>
              <button type="button" onClick={clearSearch}>Clear search</button>
            </div>
          ) : (
            <ul className="resource-list">
              {readings.map((reading) => (
                <li key={reading.association_id}><ResourceCard reading={reading} /></li>
              ))}
            </ul>
          )}
        </div>
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
