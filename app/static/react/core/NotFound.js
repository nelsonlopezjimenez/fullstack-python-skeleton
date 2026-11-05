// Chapter 3: client/src/core/NotFound.jsx (HTMX version: app/templates/not_found.html)
import { Link, html, useLocation } from '/static/vendor/react-all.js'

const NotFound = () => {
  const { pathname } = useLocation()
  return html`
    <section className="card center">
      <h2>Page not found</h2>
      <p className="muted">There is no page at <code>${pathname}</code>.</p>
      <${Link} className="button" to="/">Go home</${Link}>
    </section>
  `
}

export default NotFound
