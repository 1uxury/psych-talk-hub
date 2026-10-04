/** Reading is an event association; render in the order supplied by the API. */
export default function ResourceCard({ reading }) {
  return (
    <article className="resource-card" aria-labelledby={`reading-${reading.association_id}-title`}>
      <p className="resource-type">
        {reading.resource_type === 'research_paper' ? 'Research paper' : 'Article / web resource'}
      </p>
      <h3 id={`reading-${reading.association_id}-title`}>{reading.title}</h3>
      <p className="resource-authors">{reading.authors || 'Author not provided'}</p>
      <p className="resource-year">{reading.year ?? 'Year not provided'}</p>
      {reading.recommendation && (
        <div className="reading-recommendation">
          <h4>Why this reading?</h4>
          <p className="reading-text">{reading.recommendation}</p>
        </div>
      )}
      <a className="primary-link" href={reading.original_url}
        target="_blank" rel="noopener noreferrer"
        aria-label={`Read original: ${reading.title} (opens in a new tab)`}>
        Read original
      </a>
    </article>
  )
}
