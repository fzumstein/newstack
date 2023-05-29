import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:sio_app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        reload_includes=["*.html", "*.js", "*.css"],
    )
