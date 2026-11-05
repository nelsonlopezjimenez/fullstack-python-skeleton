// Chapter 3: client/src/App.jsx (without MUI's ThemeProvider: the look comes from /static/style.css)
import { BrowserRouter } from 'react-router'
import MainRouter from './MainRouter.jsx'

const App = () => (
  <BrowserRouter basename="/react-jsx">
    <MainRouter />
  </BrowserRouter>
)

export default App
