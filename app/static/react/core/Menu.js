// Chapter 3: client/src/core/Menu.jsx (HTMX version: app/templates/_menu.html)
import { Fragment, NavLink, html, useLocation, useNavigate } from '/static/vendor/react-all.js'
import auth from '../auth/auth-helper.js'

const Menu = () => {
  const navigate = useNavigate()
  // Re-render on every page change, so the buttons update right after signing in or out.
  useLocation()

  const jwt = auth.isAuthenticated()

  // [BEGINNER] NavLink adds class="active" on the current page; style.css colours it
  // (.appbar nav a.active), the same rule the HTMX menu uses.
  return html`
    <header className="appbar">
      <span className="brand">React Skeleton</span>
      <nav>
        <${NavLink} to="/" end>Home</${NavLink}>
        <${NavLink} to="/users" end>Users</${NavLink}>
        ${jwt ? html`
          <${Fragment}>
            <${NavLink} to=${`/users/${jwt.user._id}`} end>My Profile</${NavLink}>
            <button type="button" className="link" onClick=${() => auth.signout(() => navigate('/'))}>
              Sign out
            </button>
          </${Fragment}>
        ` : html`
          <${Fragment}>
            <${NavLink} to="/signup">Sign up</${NavLink}>
            <${NavLink} to="/signin">Sign In</${NavLink}>
          </${Fragment}>
        `}
      </nav>
    </header>
  `
}

export default Menu
