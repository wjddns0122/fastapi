from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test")
def test():
    return {"message": "test"}