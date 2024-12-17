from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from isbnlib import get_canonical_isbn, notisbn
from sqlalchemy import CheckConstraint, Column, create_engine, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base

DATABASE_URL = "mysql://root:toor@localhost:3360/library"

engine = create_engine(DATABASE_URL, connect_args={"charset": "utf8mb4"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    bookID = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    edition = Column(Integer, CheckConstraint("edition>0"), default=1)
    author = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=False)
    isbn = Column(String(13))
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
    edition: Optional[int] = Field(gt=0, default=1)
    author: str
    publisher: str
    year: Optional[int] = None
    qty: Optional[int] = Field(ge=0, default=0)
    isbn: Optional[str] = None

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
        isbn = None if notisbn(book.isbn) else get_canonical_isbn(book.isbn)
    )
    db.add(newBook)
    db.commit()
    db.refresh(newBook)
    return newBook

@app.put("/books/{book_id}", response_model=BookGet)
def update_book(book_id: int, db: Session = Depends(get_db), title: Optional[str] = None, author: Optional[str] = None, publisher: Optional[str] = None, isbn: Optional[str] = None, year: Optional[int] = None, qty: int = None):
    book = db.query(Book).filter(Book.bookID == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    #if qty is None:
    #    raise HTTPException(status_code=400, detail="why is qty none i definitely assigned it")
    
    # not letting user update edition bc different editions would ideally be different book entries entirely
    if title is not None:
        book.title = title
    if author is not None:
        book.author = author
    if isbn is not None and not notisbn(isbn):
        book.isbn = get_canonical_isbn(isbn)
    if publisher is not None:
        book.publisher = publisher
    if year is not None:
        book.year = year
    if (qty is not None) and (qty >= 0):
        book.qty = qty

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