// Chapter 3: client/src/auth/PrivateRoute.jsx
import { Navigate, Outlet, useLocation } from 'react-router'
import auth from './auth-helper.js'

const PrivateRoute = () => {
  const location = useLocation()

  if (!auth.isAuthenticated()) {
    return <Navigate to="/signin" replace state={{ from: location }} />
  }
  return <Outlet />
}

export default PrivateRoute
