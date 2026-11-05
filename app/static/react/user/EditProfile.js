// Chapter 3: client/src/user/EditProfile.jsx (HTMX version: app/templates/edit_profile.html)
import { Link, Navigate, html, useEffect, useLocation, useNavigate, useParams, useState } from '/static/vendor/react-all.js'
import auth from '../auth/auth-helper.js'
import { read, update } from './api-user.js'
import FormError from '../core/FormError.js'

// The CLASSIC pattern on purpose, as in Chapter 3: controlled inputs (value + onChange).
// Signin/Signup use React 19 form actions instead.
const EditProfile = () => {
  const { userId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [values, setValues] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [redirectToSignin, setRedirectToSignin] = useState(false)
  const jwt = auth.isAuthenticated()

  useEffect(() => {
    const controller = new AbortController()
    read(userId, jwt.token, controller.signal).then((data) => {
      if (controller.signal.aborted) return
      if (data.status === 401) setRedirectToSignin(true)
      else if (data.error) setError(data.error)
      else setValues((v) => ({ ...v, name: data.name, email: data.email }))
    })
    return () => controller.abort()
  }, [userId])

  const handleChange = (name) => (event) => {
    setValues((v) => ({ ...v, [name]: event.target.value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const user = {
      name: values.name || undefined,
      email: values.email || undefined,
      password: values.password || undefined
    }
    const data = await update(userId, jwt.token, user)
    if (data.status === 401) return setRedirectToSignin(true)
    if (data.error) return setError(data.error)
    navigate(`/users/${data._id}`)
  }

  if (redirectToSignin) {
    return html`<${Navigate} to="/signin" replace state=${{ from: location }} />`
  }

  return html`
    <section className="card">
      <h2 className="card-title">Edit Profile</h2>
      <form onSubmit=${handleSubmit} noValidate>
        <label>Name
          <input value=${values.name} onChange=${handleChange('name')} autoComplete="name" />
        </label>
        <label>Email
          <input type="email" value=${values.email} onChange=${handleChange('email')} autoComplete="email" />
        </label>
        <label>New password
          <input type="password" value=${values.password} onChange=${handleChange('password')}
            placeholder="Leave blank to keep the current one" autoComplete="new-password" />
        </label>
        <${FormError} message=${error} />
        <div className="actions">
          <button type="submit">Save</button>
          <${Link} className="button secondary" to=${`/users/${userId}`}>Cancel</${Link}>
        </div>
      </form>
    </section>
  `
}

export default EditProfile
