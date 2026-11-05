// Chapter 3: client/src/core/request.js (the same code, minus Vite's import.meta.env).

// [BEGINNER] Relative URLs (/api/users): the API is on the same server that sent this page.
// Chapter 3 read VITE_API_URL here; without a build step there is nothing to fill it in.
const API_URL = ''

/**
 * Call the API and return the parsed JSON.
 * Never throws: failures come back as { error: 'message' }, the shape the components check
 * with `if (data.error)`.
 */
export async function request(path, { method = 'GET', body, token, signal } = {}) {
  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  try {
    const response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: 'include',
      signal
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) {
      return { ...data, error: data.error ?? `Request failed (${response.status})`, status: response.status }
    }
    return data
  } catch (err) {
    return { error: err.name === 'AbortError' ? 'Request cancelled' : 'Cannot reach the server' }
  }
}
