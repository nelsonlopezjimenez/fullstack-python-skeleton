// Chapter 3: client/src/main.jsx. Compiled in the browser by jsx-loader.js (demo only).
// Compare with ../react/main.js (htm, no compiler): same React, different syntax.
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
)
