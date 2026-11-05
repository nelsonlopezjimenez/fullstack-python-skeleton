// Chapter 3: client/src/core/FormError.jsx
const FormError = ({ message }) => {
  if (!message) return null
  return <p className="error" role="alert">{message}</p>
}

export default FormError
