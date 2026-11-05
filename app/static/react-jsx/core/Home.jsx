// Chapter 3: client/src/core/Home.jsx
const Home = () => (
  <section className="card">
    <h2 className="card-title">Home Page</h2>
    <img className="media" src="/static/seashell.jpg" alt="Unicorn Shells" />
    <p>Welcome to the React Skeleton home page (JSX compiled in the browser).</p>
    <p className="muted">
      The same app: <a href="/">HTMX version</a> · <a href="/react">React with htm, no compiler</a>.
    </p>
  </section>
)

export default Home
