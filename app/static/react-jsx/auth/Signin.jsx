// Chapter 3: client/src/auth/Signin.jsx (MUI replaced by plain elements + /static/style.css)
import { useActionState } from 'react'
import { useLocation, useNavigate } from 'react-router'
import auth from './auth-helper.js'
import { signin } from './api-auth.js'
import FormError from '../core/FormError.jsx'

const Signin = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const from = location.state?.from?.pathname ?? '/'

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

  return (
    <section className="card">
      <h2 className="card-title">Sign In</h2>
      <form action={formAction}>
        <label>Email
          <input name="email" type="email" required defaultValue={state.email} autoComplete="email" />
        </label>
        <label>Password
          <input name="password" type="password" required autoComplete="current-password" />
        </label>
        <FormError message={state.error} />
        <button type="submit" disabled={isPending}>{isPending ? 'Signing in…' : 'Submit'}</button>
      </form>
    </section>
  )
}

export default Signin
