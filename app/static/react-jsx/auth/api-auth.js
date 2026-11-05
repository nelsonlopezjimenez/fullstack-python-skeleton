// Chapter 3: client/src/auth/api-auth.js (unchanged: the FastAPI routes are the same)
import { request } from '../core/request.js'

export const signin = (user) =>
  request('/api/auth/sessions', { method: 'POST', body: user })

export const signout = () =>
  request('/api/auth/sessions', { method: 'DELETE' })
