import os
import threading
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Import your modules
from backend.database.database_init import init_db
from backend.database.connection import init_pool, close_pool
from backend.routers import hinteval, metrics, save_and_load

# This points to: current_folder/source/frontend/hinteval-ui
FRONTEND_DIR = os.path.join(os.getcwd(), "frontend", "hinteval-ui")

# --- Dependency Injection Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_pool()
    init_db()
    yield
    # Cleanup
    close_pool()

# --- App Setup ---
app = FastAPI(title="HintEval Agnostic API", version="3.0", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="key12345")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hinteval.router)
app.include_router(metrics.router)
app.include_router(save_and_load.router)

def run_frontend():
    """
    Runs 'npm run dev' in the frontend directory in a separate thread.
    """
    print(f"🚀 Starting Frontend in: {FRONTEND_DIR}", flush=True)
    
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
    
    try:
        subprocess.run([npm_cmd, "run", "dev"], cwd=FRONTEND_DIR, check=True)
    except FileNotFoundError:
        print("❌ Error: Node.js/npm not found. Please install Node.js.", flush=True)
    except Exception as e:
        print(f"❌ Error starting frontend: {e}", flush=True)

if __name__ == "__main__":
    import uvicorn

    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    frontend_thread.start()

    print("🦄 Starting Backend on port 8001...", flush=True)
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)