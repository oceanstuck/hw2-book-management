from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic_extra_types.isbn import ISBN
from sqlalchemy import CheckConstraint, Column, create_engine, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "mysql://root:toor@localhost:3360/library"

engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    bookID = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    edition = Column(Integer, CheckConstraint("edition>0"))
    author = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=False)
    isbn = Column(String(18))
    year = Column(Integer)
    qty = Column(Integer, CheckConstraint("qty>=0"), default=0)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookCreate(BaseModel):
    title: str
    edition: int = Field(gt=0) | None
    author: str
    publisher: str
    year: int | None = None
    qty: int = Field(ge=0, default=0)
    isbn: ISBN | None = None

class BookGet(BookCreate):
    bookID: int
    class Config:
        orm_mode = True

Base.metadata.create_all(bind=engine)

@app.get("/books", response_model=List[BookGet])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

@app.get("/books/{book_id}", response_model=BookGet)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.bookID == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=BookGet)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    newBook = Book(
        title = book.title,
        edition = book.edition,
        author = book.author,
        publisher = book.publisher,
        year = book.year,
        qty = book.qty,
        isbn = book.isbn
    )
    db.add(newBook)
    db.commit()
    db.refresh(newBook)
    return newBook

@app.put("/books/{book_id}", response_model=BookGet)
def update_book(book_id: int, book_data: BookCreate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.bookID == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = book_data.title
    book.edition = book_data.edition
    book.author = book_data.author
    book.isbn = book_data.isbn
    book.publisher = book_data.publisher
    book.year = book_data.year
    book.qty = book_data.qty

    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id:int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.bookID == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"message": f"Deleted book with ID {book_id}"}