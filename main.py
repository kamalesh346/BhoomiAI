import traceback
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, chat, recommendations, audio, health

app = FastAPI(title="Digital Sarathi API")

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        print(f"ERROR: {exc}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(audio.router, prefix="/audio", tags=["audio"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
def read_root():
    return {"message": "Digital Sarathi API is running"}


@app.head("/")
def read_root_head():
    return


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"Starting Digital Sarathi API on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
