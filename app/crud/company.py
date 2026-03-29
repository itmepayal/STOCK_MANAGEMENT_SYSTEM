from sqlalchemy.orm import Session
from app.models.company import Company

def create_company(db: Session, symbol: str, name: str, sector: str):
    company = Company(symbol=symbol, name=name, sector=sector)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def get_company_by_symbol(db: Session, symbol: str):
    return db.query(Company).filter(Company.symbol == symbol).first()