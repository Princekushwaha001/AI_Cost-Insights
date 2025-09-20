# app/main.py (example)
from fastapi import FastAPI
from app.api.routes import router  # wherever your router is defined

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

