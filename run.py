"""
Server entrypoint for Company Brain.
Run with: python run.py
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Company Brain server at http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
