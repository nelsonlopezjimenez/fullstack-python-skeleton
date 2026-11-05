// Chapter 3: client/src/auth/PrivateRoute.jsx
import { Navigate, Outlet, html, useLocation } from '/static/vendor/react-all.js'
import auth from './auth-helper.js'

// Not signed in → to /signin, remembering where the user wanted to go (Signin reads state.from).
// The HTMX version does this on the SERVER: page_user() in app/routes/pages.py.
const PrivateRoute = () => {
  const location = useLocation()

  if (!auth.isAuthenticated()) {
    return html`<${Navigate} to="/signin" replace state=${{ from: location }} />`
  }
  return html`<${Outlet} />`
}

export default PrivateRoute
