# FastAPI + htmx + Socket.IO + Bootstrap

This is a small demo of how to make modern web development fun again:

* [FastAPI](https://fastapi.tiangolo.com/): Python backend
* [htmx](https://htmx.org/): modern frontend features without writing JavaScript
* [Socket.IO](https://python-socketio.readthedocs.io/): realtime updates & hot reload
* [Bootstrap](https://getbootstrap.com/): styling

![Screenshot](/screenshot.png?raw=true)

## Local development

* Install Python >= 3.11
* Run `pip install -r requirements.txt` (best in a virtual environment)
* Run `python run.py`

## Docker-based development

* Install Docker
* Run `docker compose up`

## How to use the app

* Open http://127.0.0.1:8000 in your browser
* Click on `Add Row` to add a new row to the table with the selected value in the first two columns and the sum of them in the third column
* Realtime: Open an incognito window or another browser with the same URL: whenever you add a row in one window, it will automatically appear in the other window

## How does it work?

1. `index.html`: when you click the `Add Row` button, htmx sends a POST request via:

   ```html
   <a class="dropdown-item" hx-post="/add-table-row" hx-swap="none" hx-vals='{"value": "1"}'>1</a>
   ```
   
   Note that for anchor tags, htmx does not automatically include name/value attributes, so we have to provide them via `hx-vals`. Also, we don't want the default htmx behavior of swapping the dropdown menu with the response, so we set `hx-swap="none"`.

2. `main.py`: the `add-table-row` endpoint adds the row to the database and sends a Socket.IO message to all connected clients:

   ```python
   await sio.emit("htmx-trigger", {"event": "update-table"})
   ```
3. `index.html`: on the frontend, the Socket.IO message is translated into an htmx event: 

   ```js
   socket.on("htmx-trigger", (data) => {
       htmx.trigger(document.body, data.event);
   });
   ```

4. `table.html`: htmx causes the table section to react to the `update-table` event (via `hx-trigger`) and to reload itself (via `hx-get`):

   ```html
   <table class="table table-sm table-hover" hx-trigger="update-table from:body" hx-get="/table">
   ```

## Why Socket.IO?

Both FastAPI and htmx support WebSockets and ServerSentEvents (SSE) out of the box, while Socket.IO is built on top of the WebSocket protocol and isn't natively supported:

* For FastAPI, see: https://fastapi.tiangolo.com/advanced/websockets/ and https://github.com/sysid/sse-starlette
* For htmx, see: https://htmx.org/extensions/web-sockets/ and https://htmx.org/extensions/server-sent-events/

So why Socket.IO?

* python-socket.io provides all the plumbing and tooling in Python that you would otherwise have to build yourself:
    * `sio.emit` is all it needs to sends a message from a function, a background tasks, or from an external process (via redis or other message queues)
    * Works with a single uvicorn instance that handles both web app and Socket.IO server for development and simple production setups where a single uvicorn worker is sufficient
    * Works with every Python web framework, including synchronous ones (WSGI)
* Socket.IO provides a few features on top of WebSockets, such as rooms (to send messages to specific clients) and easy reconnection etc., see: https://Socket.IO/docs/v4/#is-socketio-still-needed-today
* Rendering templates and sending them via WebSockets/SSE isn't really baked into the backend frameworks such as FastAPI

## Hot reload

Hot reloading the frontend, i.e., reloading the browser automatically upon changes, isn't really a thing a Python. I was looking at the `middleware` branch of https://github.com/florimondmanca/arel/tree/fm/middleware, but unfortunately, the htmx requests cause an error with calculating the Content-Length header.

Fortunately, with Socket.IO in our stack, it was easy enough to build in hot reloading so you don't need to refresh the browser manually after changing an HTML template. Here's how it works:

* Uvicorn in `run.py` has been setup to watch changes in `html`, `css` and `js` files in addition to just Python files (the default). Note that this depends on the `watchfiles` package, which is installed via the `uvicorn[standard]` dependency.
* Whenever uvicorn reloads, the Socket.IO client reconnects and triggers a reload of the page (via the `connect`/`disconnect` events in `index.html`).
* Hot reloading can be disabled by setting `hotreload=False` in `main.py`.

## Deployment

This demo can easily be deployed to any service capable of running a Docker image. For example, you can deploy to Render with a single click:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
