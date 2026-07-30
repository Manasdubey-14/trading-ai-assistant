from fastapi import FastAPI
from app.api.stock import router as stock_router

app = FastAPI(
    title="Trading AI Assistant",
    version="1.0.0",
    description="AI-powered Trading Assistant Backend"
)

app.include_router(stock_router)


@app.get("/")
def root():
    return {"message": "Welcome to Trading AI Assistant 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}