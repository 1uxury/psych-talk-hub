import { Link } from 'react-router'
import { formatTalkTime } from '../utils/talks.js'

export default function TalkCard({ talk }) {
  return (
    <article className="talk-card" aria-labelledby={`talk-${talk.id}-title`}>
      {talk.is_example && <p className="example-label">Example event</p>}
      <h3 id={`talk-${talk.id}-title`}>{talk.title}</h3>
      {talk.topic && <p className="talk-topic">{talk.topic}</p>}
      <p className="talk-time">
        <time dateTime={talk.starts_at}>{formatTalkTime(talk.starts_at)}</time>
      </p>
      {talk.speaker && <p>Speaker: {talk.speaker}</p>}
      <p>{talk.resource_count} reading {talk.resource_count === 1 ? 'resource' : 'resources'}</p>
      <Link className="primary-link" to={`/events/${talk.id}`}
        aria-label={`Explore resources for ${talk.title}`}>
        Explore resources
      </Link>
    </article>
  )
}
