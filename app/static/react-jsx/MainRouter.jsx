// Chapter 3: client/src/MainRouter.jsx
import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router'
import Home from './core/Home.jsx'
import Menu from './core/Menu.jsx'
import NotFound from './core/NotFound.jsx'
import PrivateRoute from './auth/PrivateRoute.jsx'

// Each page is fetched AND compiled the first time it is opened (jsx-loader.js handles import()).
const Signin = lazy(() => import('./auth/Signin.jsx'))
const Signup = lazy(() => import('./user/Signup.jsx'))
const Users = lazy(() => import('./user/Users.jsx'))
const Profile = lazy(() => import('./user/Profile.jsx'))
const EditProfile = lazy(() => import('./user/EditProfile.jsx'))

const MainRouter = () => (
  <>
    <Menu />
    <main>
      <Suspense fallback={<p className="card muted">Loading…</p>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/users" element={<Users />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/signin" element={<Signin />} />

          <Route element={<PrivateRoute />}>
            <Route path="/users/:userId" element={<Profile />} />
            <Route path="/users/:userId/edit" element={<EditProfile />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </main>
  </>
)

export default MainRouter
