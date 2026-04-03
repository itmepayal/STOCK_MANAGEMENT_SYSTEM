from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import stocks
from app.routes import auth
from app.routes import portfolio
from app.db.database import Base, engine

app = FastAPI(title="Stock Intelligence API")

origins = [
    "https://stock-management-system-frontend-ya.vercel.app",  
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables are ready!")
    