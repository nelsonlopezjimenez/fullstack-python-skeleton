// Chapter 3: client/src/user/Users.jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { list } from './api-user.js'
import FormError from '../core/FormError.jsx'

const Users = () => {
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    list(controller.signal).then((data) => {
      if (controller.signal.aborted) return
      if (data.error) setError(data.error)
      else setUsers(data)
    })
    return () => controller.abort()
  }, [])

  return (
    <section className="card">
      <h2 className="card-title">All Users</h2>
      <FormError message={error} />
      <ul className="list">
        {users.map((item) => (
          <li key={item._id}>
            <Link to={`/users/${item._id}`}>
              <span className="avatar">{item.name.slice(0, 1).toUpperCase()}</span>{item.name}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}

export default Users
