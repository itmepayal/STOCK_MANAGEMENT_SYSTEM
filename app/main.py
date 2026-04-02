from fastapi import FastAPI
from app.routes import stocks
from app.routes import auth
from app.routes import portfolio
from app.db.database import Base, engine

app = FastAPI(title="Stock Intelligence API")

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables are ready!")
    
    