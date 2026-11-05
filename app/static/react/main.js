// Chapter 3: client/src/main.jsx
//
// [BEGINNER] Every file in this client is a plain ES module that the browser loads as it is:
// no Vite, no Node, no build. Two things look different from the Chapter 3 code:
//   1. Imports name a real file: '/static/vendor/react-all.js' instead of 'react'. Without a bundler
//      the browser needs a path, and it needs the .js extension.
//   2. No JSX. htm's html`...` template does the same job in plain JavaScript:
//        JSX:  <App />                    htm:  html`<${App} />`
//        JSX:  <p className="x">{text}</p>  htm:  html`<p className="x">${text}</p>`
//      ${...} is a normal template-literal hole, the same as {...} in JSX.
import { StrictMode, createRoot, html } from '/static/vendor/react-all.js'
import App from './App.js'

createRoot(document.getElementById('root')).render(html`
  <${StrictMode}>
    <${App} />
  </${StrictMode}>
`)
