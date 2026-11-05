// Chapter 3: client/src/auth/Signin.jsx (HTMX version: app/templates/signin.html)
import { html, useActionState, useLocation, useNavigate } from '/static/vendor/react-all.js'
import auth from './auth-helper.js'
import { signin } from './api-auth.js'
import FormError from '../core/FormError.js'

const Signin = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const from = location.state?.from?.pathname ?? '/'

  // React 19 form action: see the comments in Chapter 3's Signin.jsx.
  const [state, formAction, isPending] = useActionState(
    async (previousState, formData) => {
      const user = {
        email: formData.get('email'),
        password: formData.get('password')
      }
      const data = await signin(user)
      if (data.error) {
        return { error: data.error, email: user.email }
      }
      auth.authenticate(data, () => navigate(from, { replace: true }))
      return { error: '', email: '' }
    },
    { error: '', email: '' }
  )

  // [BEGINNER] Attribute names are React's, as in JSX: autoComplete, defaultValue, htmlFor.
  return html`
    <section className="card">
      <h2 className="card-title">Sign In</h2>
      <form action=${formAction}>
        <label>Email
          <input name="email" type="email" required defaultValue=${state.email} autoComplete="email" />
        </label>
        <label>Password
          <input name="password" type="password" required autoComplete="current-password" />
        </label>
        <${FormError} message=${state.error} />
        <button type="submit" disabled=${isPending}>${isPending ? 'Signing in…' : 'Submit'}</button>
      </form>
    </section>
  `
}

export default Signin
