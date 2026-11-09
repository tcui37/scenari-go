from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
