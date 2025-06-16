from fastapi import FastAPI, Request
from src.app import handler
import uvicorn
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = FastAPI()

@app.post("/opsgenie-alert")
async def webhook(request: Request):
    body = await request.body()
    event = {"body": body.decode(), "headers": dict(request.headers)}
    return handler(event, None)

if __name__ == "__main__":
    uvicorn.run(
        "src.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",    
    )
