// Chapter 3: client/src/user/Profile.jsx
import { useEffect, useState } from 'react'
import { Link, Navigate, useLocation, useParams } from 'react-router'
import DeleteUser from './DeleteUser.jsx'
import auth from '../auth/auth-helper.js'
import { read } from './api-user.js'
import FormError from '../core/FormError.jsx'

const Profile = () => {
  const { userId } = useParams()
  const location = useLocation()
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')
  const [redirectToSignin, setRedirectToSignin] = useState(false)
  const jwt = auth.isAuthenticated()

  useEffect(() => {
    const controller = new AbortController()
    setError('')
    read(userId, jwt.token, controller.signal).then((data) => {
      if (controller.signal.aborted) return
      if (data.status === 401) setRedirectToSignin(true)
      else if (data.error) setError(data.error)
      else setUser(data)
    })
    return () => controller.abort()
  }, [userId])

  if (redirectToSignin) {
    return <Navigate to="/signin" replace state={{ from: location }} />
  }

  const isOwnProfile = user && jwt.user._id === user._id

  return (
    <section className="card">
      <h2 className="card-title">Profile</h2>
      <FormError message={error} />
      {user && (
        <div>
          <div className="profile">
            <span className="avatar big">{user.name.slice(0, 1).toUpperCase()}</span>
            <div>
              <p className="name">{user.name}</p>
              <p className="muted">{user.email}</p>
            </div>
          </div>
          <p className="muted">Joined: {new Date(user.created).toDateString()}</p>
          {isOwnProfile && (
            <div className="actions">
              <Link className="button" to={`/users/${user._id}/edit`}>Edit</Link>
              <DeleteUser userId={user._id} />
            </div>
          )}
        </div>
      )}
    </section>
  )
}

export default Profile
