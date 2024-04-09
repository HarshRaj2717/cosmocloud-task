# TODO Create venv
# TODO add all stuff into separate files as per the standard stricture

from fastapi import FastAPI

from routers import students

app = FastAPI()

app.include_router(students.router)
