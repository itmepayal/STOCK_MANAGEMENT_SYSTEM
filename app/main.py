# main.py
from fastapi import FastAPI
from app.routes import stock_routes
from app.routes import auth_routes
from app.db.database import Base, engine

app = FastAPI(title="Stock Intelligence API")

app.include_router(auth_routes.router)
app.include_router(stock_routes.router)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables are ready!")
    