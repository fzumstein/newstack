from pathlib import Path

import socketio
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

hotreload = True
this_dir = Path(__file__).parent
templates = Jinja2Templates(directory=this_dir / "templates")

app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi")
# sio_app forwards non-socketio requests to app. This allows you to run them with a
# single uvicorn server as long as you're only using a single worker.
sio_app = socketio.ASGIApp(sio, app)

# Fake database
db = []


def get_data():
    """Adds the calculated third column"""
    if db:
        return [row + [sum((row[0], row[1]))] for row in db]
    return []


# Endpoints
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "hotreload": hotreload, "values": get_data()},
    )


@app.get("/table")
async def table(request: Request):
    return templates.TemplateResponse(
        "_table.html", {"request": request, "values": get_data()}
    )


@app.post("/add-table-row")
async def add_table_row(value: int = Form()):
    db.append([value, value])
    await sio.emit("trigger-event", {"event": "update-table"})
    return HTMLResponse(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/clear-table")
async def clear_table():
    db.clear()
    await sio.emit("trigger-event", {"event": "update-table"})
    return HTMLResponse(status_code=status.HTTP_204_NO_CONTENT)


# Socket.io
@sio.event
async def connect(sid, environ, auth):
    """Authentication would be handled here"""
    print("connect ", sid)


@sio.event
async def disconnect(sid):
    print("disconnect ", sid)
