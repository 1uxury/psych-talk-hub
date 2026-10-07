import { Link } from 'react-router'

export default function NotFoundPage({ talk = false }) {
  return (
    <section>
      <h1>{talk ? "We couldn't find this talk." : "We couldn't find this page."}</h1>
      <Link to="/">Back to talks</Link>
    </section>
  )
}
