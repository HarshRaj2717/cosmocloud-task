# TODO Create venv stuff

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Heello World"}
