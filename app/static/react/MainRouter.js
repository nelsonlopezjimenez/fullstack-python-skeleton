// Chapter 3: client/src/MainRouter.jsx
import { Fragment, Route, Routes, Suspense, html, lazy } from '/static/vendor/react-all.js'
import Home from './core/Home.js'
import Menu from './core/Menu.js'
import NotFound from './core/NotFound.js'
import PrivateRoute from './auth/PrivateRoute.js'

// [BEGINNER] Code splitting works without a bundler: import() is built into the browser, so each
// page file is downloaded the first time that page is opened (open DevTools > Network to see it).
const Signin = lazy(() => import('./auth/Signin.js'))
const Signup = lazy(() => import('./user/Signup.js'))
const Users = lazy(() => import('./user/Users.js'))
const Profile = lazy(() => import('./user/Profile.js'))
const EditProfile = lazy(() => import('./user/EditProfile.js'))

// [BEGINNER] htm: element=${html`<${Home} />`} is JSX's element={<Home />}.
const MainRouter = () => html`
  <${Fragment}>
    <${Menu} />
    <main>
      <${Suspense} fallback=${html`<p className="card muted">Loading…</p>`}>
        <${Routes}>
          <${Route} path="/" element=${html`<${Home} />`} />
          <${Route} path="/users" element=${html`<${Users} />`} />
          <${Route} path="/signup" element=${html`<${Signup} />`} />
          <${Route} path="/signin" element=${html`<${Signin} />`} />

          <${Route} element=${html`<${PrivateRoute} />`}>
            <${Route} path="/users/:userId" element=${html`<${Profile} />`} />
            <${Route} path="/users/:userId/edit" element=${html`<${EditProfile} />`} />
          </${Route}>

          <${Route} path="*" element=${html`<${NotFound} />`} />
        </${Routes}>
      </${Suspense}>
    </main>
  </${Fragment}>
`

export default MainRouter
