// Chapter 3: client/src/user/Signup.jsx (HTMX version: app/templates/signup.html)
import { Fragment, Link, html, useActionState } from '/static/vendor/react-all.js'
import { create } from './api-user.js'
import FormError from '../core/FormError.js'

const initialState = { error: '', open: false, values: { name: '', email: '' } }

const Signup = () => {
  const [state, formAction, isPending] = useActionState(async (previousState, formData) => {
    const user = Object.fromEntries(formData)
    const data = await create(user)
    if (data.error) {
      return { error: data.error, open: false, values: { name: user.name, email: user.email } }
    }
    return { ...initialState, open: true }
  }, initialState)

  // No `required` on purpose (as in Chapter 3): an empty form shows the server's messages.
  return html`
    <${Fragment}>
      <section className="card">
        <h2 className="card-title">Sign Up</h2>
        <form action=${formAction}>
          <label>Name <input name="name" defaultValue=${state.values.name} autoComplete="name" /></label>
          <label>Email <input name="email" type="email" defaultValue=${state.values.email} autoComplete="email" /></label>
          <label>Password <input name="password" type="password" autoComplete="new-password" /></label>
          <${FormError} message=${state.error} />
          <button type="submit" disabled=${isPending}>Submit</button>
        </form>
      </section>

      ${state.open && html`
        <div className="backdrop">
          <div className="card dialog" role="dialog" aria-modal="true" aria-labelledby="new-account">
            <h2 id="new-account">New Account</h2>
            <p>New account successfully created.</p>
            <div className="actions">
              <${Link} className="button" to="/signin" autoFocus>Sign In</${Link}>
            </div>
          </div>
        </div>
      `}
    </${Fragment}>
  `
}

export default Signup
