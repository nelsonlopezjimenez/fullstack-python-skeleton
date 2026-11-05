// Chapter 3: client/src/core/NotFound.jsx
import { Link, useLocation } from 'react-router'

const NotFound = () => {
  const { pathname } = useLocation()
  return (
    <section className="card center">
      <h2>Page not found</h2>
      <p className="muted">There is no page at <code>{pathname}</code>.</p>
      <Link className="button" to="/">Go home</Link>
    </section>
  )
}

export default NotFound
