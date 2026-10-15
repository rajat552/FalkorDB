"""
Server entrypoint for Company Brain.
Run with: python run.py
"""
import sys
import uvicorn
from app.config import SERVER_HOST, SERVER_PORT

if __name__ == "__main__":
    reload_enabled = "--reload" in sys.argv
    print(f"Starting Company Brain server at http://{SERVER_HOST}:{SERVER_PORT} ...")
    uvicorn.run("app.main:app", host=SERVER_HOST, port=SERVER_PORT, reload=reload_enabled)
