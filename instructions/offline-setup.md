# Offline setup (no internet, no Node.js)

How to get this project running on lab machines that have **no internet access**. The idea is the
same as with Verdaccio for npm: download everything once on a machine that is online, then copy it
over.

```
 ONLINE machine                                   OFFLINE lab machine
 ──────────────                                   ───────────────────
 python.org installer (.exe)      ── USB / share ──►  install Python 3.14
 tools\build-wheelhouse.ps1 -Zip  ── USB / share ──►  unzip as wheelhouse\
 git clone / Gitea                ── LAN ─────────►  tools\install-offline.ps1
                                                      python -m pytest
                                                      python -m uvicorn app.main:app --reload
```

## npm ↔ pip, side by side

| Job | npm | pip |
|---|---|---|
| Project-local packages | `node_modules/` (automatic) | `.venv/` (**you create it**: `python -m venv .venv`) |
| Download without installing | `npm cache add` / `npm pack` | `pip download -d wheelhouse ...` |
| Install from local files only | `npm install --offline` | `pip install --no-index --find-links wheelhouse ...` |
| Private registry / caching proxy | Verdaccio | devpi (proxy + private), pypiserver (serves a folder) |
| Point the tool at the registry | `.npmrc`: `registry=http://...` | `pip.ini`: `index-url = http://.../simple/` |
| Package file | `.tgz` (almost always plain JS) | `.whl` (**may contain compiled code for one OS, CPU and Python version**) |

The last row is the important difference. Most npm packages run anywhere. A wheel such as
`pydantic_core-2.50.2-cp314-cp314-win_amd64.whl` only installs on **CPython 3.14, Windows, 64-bit**.
The name says so: `cp314` is the Python version and `win_amd64` is the platform. Pure-Python
wheels end in `py3-none-any.whl` and work everywhere. This project has only three compiled wheels:
`pydantic_core`, `pymongo` and `MarkupSafe`.

## 1. Python itself

Download the **Windows installer (64-bit)** for the latest Python 3.14.x from python.org on the
online machine. It installs offline, and it already contains pip and the `py` launcher.

Interactive install: tick **"Add python.exe to PATH"**. On the last screen, click **"Disable path
length limit"** (it needs admin). Long `.venv` paths can otherwise fail with
`[WinError 206] The filename or extension is too long`.

Silent install for a whole lab:
```powershell
python-3.14.x-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_launcher=1
```

Check it:
```powershell
py -0p                 # every Python on this machine, with its path
python --version
python -m pip --version
```

**Don't use the "embeddable package" (.zip)**. It has no pip and no venv. Use the installer.

### When pip is missing

| Symptom | Fix (all of these work offline) |
|---|---|
| `pip` is not recognized, but `python` works | Always use `python -m pip ...`. It finds the pip that belongs to that exact Python. |
| `No module named pip` | `python -m ensurepip --upgrade`: pip is **bundled inside Python**, so no download is needed. |
| `No module named ensurepip` (some Linux builds, embeddable zip) | Use the `pip-*.whl` in the wheelhouse. `tools\install-offline.ps1` does this for you (step 3). By hand: `$env:PYTHONPATH="wheelhouse\pip-26.3-py3-none-any.whl"; .venv\Scripts\python -m pip install --no-index wheelhouse\pip-26.3-py3-none-any.whl` |
| Debian/Ubuntu: `ensurepip is not available` | `sudo apt install python3-venv python3-pip` (offline: copy the `.deb` files and install them with `apt install ./*.deb`) |
| `externally-managed-environment` (Linux) | Not a bug: the system Python refuses global installs. Use a venv. |

## 2. Build the wheelhouse (online machine)

```powershell
powershell -ExecutionPolicy Bypass -File tools\build-wheelhouse.ps1 -Zip
```

This downloads every package in `requirements-dev.txt`, plus pip itself, for **Python 3.14 on
win_amd64**. The result is `wheelhouse\` and `wheelhouse-win_amd64-py3.14.zip` (about 9 MB, 34 wheels).
The online machine can run any Python version, because it only downloads.

Other targets:
```powershell
tools\build-wheelhouse.ps1 -Platform manylinux2014_x86_64 -Out wheelhouse    # Linux PCs, same folder
tools\build-wheelhouse.ps1 -Platform macosx_11_0_arm64    -Out wheelhouse    # Apple Silicon Macs
tools\build-wheelhouse.ps1 -PythonVersion 3.13                               # a lab still on 3.13
```

One folder can hold several platforms, and pip picks the matching wheel on each machine.

Without the script (bash or PowerShell, same flags):
```bash
python -m pip download -r requirements-dev.txt -d wheelhouse \
  --only-binary=:all: --platform win_amd64 --python-version 3.14 --implementation cp --ignore-requires-python
python -m pip download pip -d wheelhouse --only-binary=:all: --no-deps
```

## 3. Install on the offline machine

Copy the repo (clone from Gitea on the LAN) and unzip the wheelhouse next to it as `wheelhouse\`.
Then:

```powershell
powershell -ExecutionPolicy Bypass -File tools\install-offline.ps1
```

The script finds Python 3.14, creates `.venv`, repairs pip if needed, installs from `wheelhouse\`
with `--no-index` (pip never tries the internet) and creates `.env`.

By hand:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Git Bash: source .venv/Scripts/activate · Linux/macOS: source .venv/bin/activate
python -m pip install --no-index --find-links wheelhouse --ignore-requires-python -r requirements-dev.txt
copy .env.example .env
python -m pytest
python -m uvicorn app.main:app --reload --port 8000
```

`Activate.ps1 cannot be loaded because running scripts is disabled`: run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or skip activation and call
`.venv\Scripts\python.exe` directly. Activation only puts that folder first on the PATH.

## 4. Or: a package server on the LAN (the Verdaccio way)

Copying a folder to every machine works for a small lab. With many machines, run one server and
point everyone's pip at it.

### pypiserver: serves a wheelhouse folder

```powershell
# On the server (it needs pypiserver itself, which is in no requirements file here):
python -m pip install pypiserver            # online, or --no-index --find-links from a wheelhouse
python -m pypiserver run -p 8080 -i 0.0.0.0 .\wheelhouse
```

### devpi: a caching proxy, closest to Verdaccio

While the server still has internet, every package someone installs through it is cached. After
that it keeps serving the cache offline. It can also host your own packages.
```powershell
python -m pip install devpi-server
devpi-init
devpi-server --host 0.0.0.0 --port 3141     # index URL: http://SERVER:3141/root/pypi/+simple/
```

### Pointing pip at the server (like `npm config set registry`)

```powershell
python -m pip config set global.index-url http://192.168.1.10:8080/simple/
python -m pip config set global.trusted-host 192.168.1.10    # needed because it is http, not https
# written to %APPDATA%\pip\pip.ini (Linux/macOS: ~/.config/pip/pip.conf)
# one command only:   python -m pip install --index-url http://192.168.1.10:8080/simple/ ...
# one shell only:     $env:PIP_INDEX_URL = "http://192.168.1.10:8080/simple/"
```

**Gitea** also has a PyPI registry (`/api/packages/<owner>/pypi`), but it only hosts packages you
upload with `twine`. It doesn't proxy or cache PyPI, so it can't replace devpi or a wheelhouse.

## 5. MongoDB

Nothing changes from the Node chapters: same server, same URI with `?directConnection=true`. This
app uses its own database names (`pythonskeleton`, and `pythonskeleton_test` for pytest). The tests
that need MongoDB are **skipped**, not failed, when it isn't running.

## Pitfalls

- **Don't copy `.venv` to another machine.** It contains absolute paths to the Python that created
  it. Copy the wheelhouse and create a new `.venv` on each machine; it takes seconds.
- **Wrong Python version or platform:** `No matching distribution found for pydantic_core==...`
  with `--no-index` almost always means the wheelhouse was built for another Python version or
  platform. Check `python --version` and the `cp3XX`/platform part of the wheel names.
- **Mixed platforms, one requirements file:** `pip download --platform` checks conditions such as
  `; sys_platform == "win32"` against the machine that runs the download, not the target. This
  project has none that matter, but a Linux wheelhouse built on Windows may contain an extra
  `colorama` wheel. That is harmless.
- **Long paths on Windows:** keep repos in short folders (`C:\labs\...`) or enable long paths
  (see section 1).
- **`pip` vs `python -m pip`:** with several Pythons installed (python.org, Microsoft Store,
  Anaconda), bare `pip` can belong to a different Python than `python`. `python -m pip` is never
  ambiguous.
