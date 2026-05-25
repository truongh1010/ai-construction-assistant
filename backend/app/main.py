from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import issues

app = FastAPI(title="AI Construction Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# register issues router in FastAPI
app.include_router(issues.router)

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Consctruction Assistant API is running"
    }
