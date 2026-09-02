from fastapi import FastAPI

app = FastAPI(
    title="SQL AI Agent",
    version="1.0"
)

@app.get("/")
def home():

    return {
        "Application": "SQL AI Agent",
        "Version": "1.0"
    }

@app.get("/health")
def health():

    return {
        "Status": "Healthy"
    }