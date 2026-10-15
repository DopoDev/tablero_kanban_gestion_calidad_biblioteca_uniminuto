from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import auth, books, loans, readers, reports, reservations


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Biblioteca Villa de los Estudiantes", lifespan=lifespan)
app.mount("/public", StaticFiles(directory="public"), name="public")
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(readers.router)
app.include_router(loans.router)
app.include_router(reservations.router)
app.include_router(reports.router)


@app.get("/")
def home():
    return {"message": "Biblioteca"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
