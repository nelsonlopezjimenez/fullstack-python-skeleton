// The in-browser JSX demo: fetch a .jsx file → compile it with Babel → run it as an ES module.
// In about 60 lines, this is the job Vite does on the developer's machine in Chapter 3.
//
// [BEGINNER] DEMO ONLY. Every visitor downloads Babel (2.4 MB) and compiles every file on every
// page load, and the page needs a weaker Content-Security-Policy (see app/main.py). Real projects
// compile JSX ONCE, before deploying (vite build), and send plain JavaScript.
//
// [ADVANCED] Why not the usual <script type="text/babel" src="App.jsx">? That runs each file as a
// separate script, so `import Menu from './core/Menu.jsx'` cannot work: the browser would fetch
// Menu.jsx itself and choke on the JSX. This loader compiles imported .jsx files first and hands
// the browser the compiled code as blob: URLs, so the .jsx files keep Chapter 3's import lines.
/* global Babel */ // set by /static/vendor/babel.min.js, loaded before this module

const VENDOR = new URL('/static/vendor/react-all.js', location.href).href

// [BEGINNER] Package names → files, like Vite's dependency resolution (or an import map).
const PACKAGES = {
  react: VENDOR,
  'react/jsx-runtime': VENDOR, // what compiled JSX imports: jsx(), jsxs()
  'react-dom/client': VENDOR,
  'react-router': VENDOR
}

const resolve = (specifier, fromUrl) => PACKAGES[specifier] ?? new URL(specifier, fromUrl).href

// One compile per file, so a .jsx file imported by several others is still ONE module.
const compiled = new Map() // .jsx URL → Promise of its blob: URL

function compile(url) {
  if (!compiled.has(url)) compiled.set(url, compileUncached(url))
  return compiled.get(url)
}

async function compileUncached(url) {
  const response = await fetch(url)
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}: ${url}`)
  const jsxImports = []
  const { code } = Babel.transform(await response.text(), {
    filename: url,
    sourceType: 'module',
    presets: [['react', { runtime: 'automatic' }]], // <p/> → jsx('p', ...), the same as Vite
    plugins: [rewriteImports(url, jsxImports)],
    sourceMaps: 'inline' // DevTools > Sources shows the original JSX
  })
  // The .jsx files this one imports must exist (as blob: URLs) before it can run.
  const blobUrls = await Promise.all(jsxImports.map(compile))
  let output = code.replaceAll('"react/jsx-runtime"', JSON.stringify(VENDOR))
  jsxImports.forEach((dep, i) => { output = output.replaceAll(`__JSX__${dep}`, blobUrls[i]) })
  return URL.createObjectURL(new Blob([output], { type: 'text/javascript' }))
}

// A Babel plugin: make every import specifier a full URL (a blob: module has no folder of its own
// to resolve './x.js' against), and mark the .jsx ones for compile() above.
const rewriteImports = (fromUrl, jsxImports) => ({ types: t }) => ({
  visitor: {
    'ImportDeclaration|ExportNamedDeclaration|ExportAllDeclaration' (path) {
      const source = path.node.source
      if (!source) return
      const url = resolve(source.value, fromUrl)
      if (url.endsWith('.jsx')) {
        jsxImports.push(url)
        source.value = `__JSX__${url}`
      } else {
        source.value = url
      }
    },
    // lazy(() => import('./auth/Signin.jsx')) → compiled the first time the page is opened.
    ImportExpression (path) {
      const source = path.node.source
      if (source.type !== 'StringLiteral') return
      const url = resolve(source.value, fromUrl)
      if (url.endsWith('.jsx')) {
        path.replaceWith(t.callExpression(t.identifier('__importJsx'), [t.stringLiteral(url)]))
      } else {
        source.value = url
      }
    }
  }
})

globalThis.__importJsx = (url) => compile(url).then((blobUrl) => import(blobUrl))

try {
  await globalThis.__importJsx(new URL('./main.jsx', import.meta.url).href)
} catch (err) {
  // A JSX syntax error lands here with Babel's code frame: show it on the page, like Vite's overlay.
  const pre = document.createElement('pre')
  pre.className = 'card error'
  pre.textContent = err.message
  document.getElementById('root').replaceChildren(pre)
  throw err
}
