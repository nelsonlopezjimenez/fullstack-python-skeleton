// Chapter 3: client/src/core/Menu.jsx
import { NavLink, useLocation, useNavigate } from 'react-router'
import auth from '../auth/auth-helper.js'

const Menu = () => {
  const navigate = useNavigate()
  useLocation()

  const jwt = auth.isAuthenticated()

  return (
    <header className="appbar">
      <span className="brand">React Skeleton · JSX</span>
      <nav>
        <NavLink to="/" end>Home</NavLink>
        <NavLink to="/users" end>Users</NavLink>
        {jwt ? (
          <>
            <NavLink to={`/users/${jwt.user._id}`} end>My Profile</NavLink>
            <button type="button" className="link" onClick={() => auth.signout(() => navigate('/'))}>
              Sign out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/signup">Sign up</NavLink>
            <NavLink to="/signin">Sign In</NavLink>
          </>
        )}
      </nav>
    </header>
  )
}

export default Menu
