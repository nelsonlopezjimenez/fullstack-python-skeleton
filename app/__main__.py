"""`python -m app` starts the server (Chapter 3: server/server.js and `npm start`)."""
import uvicorn

from app.config import settings

# [BEGINNER] This block runs only when the file is executed (python -m app), not when it is
# imported. In development use `python -m uvicorn app.main:app --reload --port 8000` instead:
# --reload restarts the server when a file changes, like nodemon.
if __name__ == "__main__":
    # [ADVANCED] host 127.0.0.1 = only this machine can connect. Use "0.0.0.0" to accept
    # connections from the classroom network.
    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.port)
