// Everything the React client imports, in ONE browser-ready ES module (app/static/vendor/react-all.js).
//
// [BEGINNER] React 19 is published for bundlers (CommonJS), not as a file a browser can load.
// esbuild turns these packages into one ES module once, on the maintainer's machine, and the
// result is committed like htmx.min.js. The browser then imports it with a plain <script type="module">.
//
// [ADVANCED] One file, so there is exactly ONE copy of React: react-router and react-dom must use
// the same React instance as the components, or hooks fail ("Invalid hook call").
import * as React from 'react'
import htm from 'htm'

export default React

// [ADVANCED] react is CommonJS, so its exports are listed by hand: an ES module needs names it
// can know before the code runs. Add a name here (and rebuild) if a component needs another one.
export const {
  Fragment, StrictMode, Suspense, createContext, createElement, lazy, memo, startTransition, use,
  useActionState, useCallback, useContext, useEffect, useId, useMemo, useOptimistic, useReducer,
  useRef, useState, useTransition
} = React

export { createRoot } from 'react-dom/client'

export {
  BrowserRouter, Link, Navigate, NavLink, Outlet, Route, Routes, useLocation, useNavigate, useParams
} from 'react-router'

// [BEGINNER] htm: JSX-like tagged templates that the browser understands without a compiler.
//   JSX:  <Link to="/users">Users</Link>
//   htm:  html`<${Link} to="/users">Users</${Link}>`
export const html = htm.bind(React.createElement)
