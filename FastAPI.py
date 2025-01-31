from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
import uvicorn

# Configuració de la base de dades
DATABASE_URL = "postgresql://postgres:password@localhost:5432/Dates"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model de la base de dades
class Date(Base):
    __tablename__ = "Date"
    id = Column(Integer, primary_key=True, index=True)
    name_notari = Column(String, index=True)
    sala = Column(String)
    date_date = Column(String)
    descripcio = Column(String)

Base.metadata.create_all(bind=engine)

# Models Pydantic
class DateCreate(BaseModel):
    name_notari: str
    sala: str
    date_date: str
    descripcio: str

class DateResponse(DateCreate):
    id: int

    class Config:
        from_attributes = True

# Inicialització de FastAPI
app = FastAPI()

# Funció per obtenir la sessió de la base de dades
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/dates/", response_model=list[DateResponse])
def list_dates(db: Session = Depends(get_db)):
    """Endpoint per a llistar totes les cites."""
    return db.query(Date).all()

@app.get("/dates/insert/{name_notari}/{sala}/{date_date}/{descripcio}", response_model=DateResponse)
def insert_date(
    name_notari: str,
    sala: str,
    date_date: str,
    descripcio: str,
    db: Session = Depends(get_db)
):
    """Inserir una nova cita passant els valors per l'URL."""
    new_date = Date(
        name_notari=name_notari,
        sala=sala,
        date_date=date_date,
        descripcio=descripcio
    )
    db.add(new_date)
    db.commit()
    db.refresh(new_date)
    return new_date

@app.get("/dates/delete/{date_id}")
def delete_date(date_id: int, db: Session = Depends(get_db)):
    """Eliminar una cita passant la ID en el path."""
    date = db.query(Date).filter(Date.id == date_id).first()
    if not date:
        raise HTTPException(status_code=404, detail="Cita no trobada.")
    db.delete(date)
    db.commit()
    return {"message": f"Cita amb ID {date_id} eliminada amb èxit."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)