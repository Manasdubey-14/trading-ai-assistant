from fastapi import FastAPI

app = FastAPI(
    title="Trading AI Assistant",
    version="1.0.0",
    description="AI-powered Trading Assistant Backend"
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Trading AI Assistant 🚀"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }