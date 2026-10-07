import { useState } from 'react'
import { safeCoverImageUrl } from '../utils/coverImages.js'

function CoverImage({ src, alt, priority }) {
  const [failed, setFailed] = useState(false)
  return failed ? <CoverFallback /> : (
    <img src={src} alt={alt} width="1200" height="675"
      loading={priority ? 'eager' : 'lazy'} decoding="async" referrerPolicy="no-referrer"
      onError={() => setFailed(true)} />
  )
}

function CoverFallback() {
  return <div className="cover-fallback" aria-hidden="true">
    <span className="cover-orbit" />
    <span className="cover-fallback-label">A little curiosity. A new perspective.</span>
  </div>
}

export default function TalkCover({ talk, priority = false }) {
  const src = safeCoverImageUrl(talk.cover_image_url)
  return <div className="talk-cover">
    {src ? <CoverImage key={src} src={src} alt={talk.cover_image_alt || ''} priority={priority} />
      : <CoverFallback />}
  </div>
}
