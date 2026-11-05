// Chapter 3: client/src/core/FormError.jsx (HTMX version: app/templates/_form_error.html)
import { html } from '/static/vendor/react-all.js'

const FormError = ({ message }) => {
  if (!message) return null
  // [BEGINNER] className, not class: htm passes attributes to React unchanged, and React's
  // name for the HTML class attribute is className (the same rule as in JSX).
  return html`<p className="error" role="alert">${message}</p>`
}

export default FormError
