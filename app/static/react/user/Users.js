// Chapter 3: client/src/user/Users.jsx (HTMX version: app/templates/users.html)
import { Link, html, useEffect, useState } from '/static/vendor/react-all.js'
import { list } from './api-user.js'
import FormError from '../core/FormError.js'

const Users = () => {
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')

  // [BEGINNER] Compare with users.html: there the server had the list BEFORE it sent the page.
  // Here the page arrives empty, then this effect fetches /api/users and React fills it in.
  useEffect(() => {
    const controller = new AbortController()
    list(controller.signal).then((data) => {
      if (controller.signal.aborted) return
      if (data.error) setError(data.error)
      else setUsers(data)
    })
    return () => controller.abort()
  }, [])

  // [BEGINNER] users.map(...) returns an array of elements; each needs a stable `key`.
  return html`
    <section className="card">
      <h2 className="card-title">All Users</h2>
      <${FormError} message=${error} />
      <ul className="list">
        ${users.map((item) => html`
          <li key=${item._id}>
            <${Link} to=${`/users/${item._id}`}>
              <span className="avatar">${item.name.slice(0, 1).toUpperCase()}</span>${item.name}
            </${Link}>
          </li>
        `)}
      </ul>
    </section>
  `
}

export default Users
