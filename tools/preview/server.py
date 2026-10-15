"""Loopback-only mock harness. Run from repository root with backend's Python."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
# This entry point must never perform paid inference, even with inherited config.
os.environ['PROOFREAD_PROVIDER'] = 'mock'
from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.main import app as backend

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.get('/')
def preview():
    return FileResponse(Path(__file__).with_name('index.html'), headers={'Cache-Control': 'no-store'})

app.mount('/', backend)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8010, access_log=False)
