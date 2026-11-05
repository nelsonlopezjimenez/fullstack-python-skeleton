// Chapter 3: client/src/App.jsx (without MUI's ThemeProvider: the look comes from /static/style.css)
import { BrowserRouter, html } from '/static/vendor/react-all.js'
import MainRouter from './MainRouter.js'

// [BEGINNER] basename="/react": this client lives under /react on the FastAPI server (the HTMX
// pages own /). Links stay short, <Link to="/users">, and React Router adds the prefix itself.
const App = () => html`
  <${BrowserRouter} basename="/react">
    <${MainRouter} />
  </${BrowserRouter}>
`

export default App
