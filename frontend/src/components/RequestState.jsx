export default function RequestState({ status, context, onRetry }) {
  if (status === 'loading') {
    return (
      <div className="request-state" role="status">
        {context === 'talk' ? 'Loading resources…' : 'Loading talks…'}
      </div>
    )
  }

  if (status === 'not_found') {
    return (
      <div className="request-state">
        <p>{context === 'talk'
          ? "We couldn't find this talk." : "We couldn't find this page."}</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="request-state request-error" role="alert">
        <p>We couldn't load this page. Please try again.</p>
        <button type="button" onClick={onRetry}>Retry</button>
      </div>
    )
  }

  return null
}
