// Chapter 3: client/src/auth/auth-helper.js (unchanged)
import { signout } from './api-auth.js'

const STORAGE_KEY = 'jwt'

const isExpired = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return typeof payload.exp === 'number' && payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

// [ADVANCED] As in Chapter 3, the token lives in sessionStorage and goes out as
// "Authorization: Bearer ...". The server ALSO sets the httpOnly cookie "t" on sign-in, which the
// HTMX pages use; app/auth.py accepts either. So signing in here also signs you in on the HTMX
// pages, and the other way round only if this tab's sessionStorage has the token.
const auth = {
  isAuthenticated() {
    try {
      const jwt = JSON.parse(sessionStorage.getItem(STORAGE_KEY))
      if (!jwt?.token || isExpired(jwt.token)) return false
      return jwt
    } catch {
      return false
    }
  },

  authenticate(jwt, cb) {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(jwt))
    cb?.()
  },

  async signout(cb) {
    sessionStorage.removeItem(STORAGE_KEY)
    cb?.()
    await signout()
  }
}

export default auth
