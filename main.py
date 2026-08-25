from fastapi import FastAPI

app = FastAPI(
    title="PayPilot AI",
    description="AI-powered agentic commerce assistant",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "PayPilot AI is running!",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }