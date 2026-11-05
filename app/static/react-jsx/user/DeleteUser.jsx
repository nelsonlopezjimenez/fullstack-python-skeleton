// Chapter 3: client/src/user/DeleteUser.jsx (MUI Dialog replaced by a plain overlay)
import { useState } from 'react'
import { useNavigate } from 'react-router'
import auth from '../auth/auth-helper.js'
import { remove } from './api-user.js'
import FormError from '../core/FormError.jsx'

const DeleteUser = ({ userId }) => {
  const [open, setOpen] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const deleteAccount = async () => {
    const jwt = auth.isAuthenticated()
    const data = await remove(userId, jwt.token)
    if (data.error) {
      setError(data.error)
      return
    }
    auth.signout(() => navigate('/'))
  }

  return (
    <>
      <button type="button" className="danger" onClick={() => setOpen(true)}>Delete account</button>

      {open && (
        <div className="backdrop" onClick={() => setOpen(false)}>
          <div className="card dialog" role="dialog" aria-modal="true" aria-labelledby="delete-title"
               onClick={(event) => event.stopPropagation()}>
            <h2 id="delete-title">Delete Account</h2>
            <p>Confirm to delete your account.</p>
            <FormError message={error} />
            <div className="actions">
              <button type="button" className="button secondary" onClick={() => setOpen(false)}>Cancel</button>
              <button type="button" className="danger" onClick={deleteAccount} autoFocus>Confirm</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default DeleteUser
