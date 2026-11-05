// Chapter 3: client/src/core/Home.jsx (HTMX version: app/templates/home.html)
import { html } from '/static/vendor/react-all.js'

const Home = () => html`
  <section className="card">
    <h2 className="card-title">Home Page</h2>
    <img className="media" src="/static/seashell.jpg" alt="Unicorn Shells" />
    <p>Welcome to the React Skeleton home page.</p>
    <p className="muted">
      The same app without React: <a href="/">the HTMX version</a>. Both use the same /api and database.
    </p>
  </section>
`

export default Home
