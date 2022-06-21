from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import SessionLocal, engine
from schema import schema
from models import models
from services import db_service as dbs

from viewmodels.books import addbookviewmodel, showbooks, searchbooks
from viewmodels.authors import showauthors, authorbooks
from viewmodels.home import homeviewmodel


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", status_code=status.HTTP_200_OK)
def home_page(request: Request, db: Session = Depends((get_db))):
    vm = homeviewmodel.HomeViewModel(db=db)
    books = vm.books
    print(f'Request for home_page page received(test1)')
    return templates.TemplateResponse('home/index.html', {"request": request, "books": books}, status_code=status.HTTP_200_OK)


@app.get("/author/add", status_code=status.HTTP_200_OK)
def authors_add(request: Request):
    print(f'Request to get /author/add page received')
    return templates.TemplateResponse('authors/partials/add_authors_form.html', {"request": request})


@app.post("/authors/add", status_code=status.HTTP_201_CREATED)
def create_author(request: Request, email: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), db: Session = Depends(get_db)):
    print(f'Request to post /author/add page received with email:{email}, first_name:{first_name}, last_name:{last_name}')
    db_author = dbs.get_author_by_email(db, email=email)
    if db_author:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    author = schema.AuthorCreate(last_name=last_name, first_name=first_name, email=email)
    dbs.create_author(db=db, author=author)
    url = request.headers.get('HX-Current-URL').split('/')[-1]
    if request.headers.get('HX-Request') and url == 'authors':
        return templates.TemplateResponse('authors/partials/show_add_author_form.html', {"request": request})
    elif request.headers.get('HX-Request') and url == '':
        return templates.TemplateResponse('books/partials/show_add_form.html', {"request": request})
    else:
        pass
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/authors/cancel_add", status_code=status.HTTP_200_OK)
def cancel_author(request: Request):
    print(f'Request to get /author/cancel_add page received')

    url = request.headers.get('HX-Current-URL').split('/')[-1]
    if url == 'authors':
        return templates.TemplateResponse('authors/partials/show_add_author_form.html', {"request": request})
    return templates.TemplateResponse('books/partials/show_add_form.html', {"request": request})


@app.get("/authors/close_books/{author_id}", status_code=status.HTTP_200_OK)
def close_authors_books(request: Request, author_id: int):
    print(f'Request to get /authors/close_books/ page received with author_id:{author_id}')
    return templates.TemplateResponse('authors/partials/show_books.html', {"request": request, "author_id": author_id})


@app.get("/authors", status_code=status.HTTP_200_OK)
def show_authors(request: Request, db: Session = Depends(get_db)):
    print(f'Request to get /authors page received')
    vm = showauthors.ShowAuthorsViewModel(db=db)
    authors = vm.authors
    return templates.TemplateResponse('authors/authors.html', {"request": request, "authors": authors})


@app.get("/author/books/{author_id}", status_code=status.HTTP_200_OK)
def authors_books(request: Request, author_id: int, db: Session = Depends(get_db)):
    print(f'Request to get /author/books page received with author_id:{author_id}')
    vm = authorbooks.AuthorBooksViewModel(db=db, author_id=author_id)
    books = vm.books
    return templates.TemplateResponse('authors/partials/authors_books.html',
                                      {"request": request, "books": books, "author_id": author_id})


@app.get("/books/add", status_code=status.HTTP_200_OK)
def add_book(request: Request, db: Session = Depends(get_db)):
    print(f'Request to get /books/add page received')
    vm = addbookviewmodel.AddBookViewModel(db=db)
    data = vm.to_dict()
    return templates.TemplateResponse('books/partials/add_books_form.html', {"request": request, "data": data})


@app.post("/books/add", status_code=status.HTTP_201_CREATED)
def book_add(title: str = Form(...), pages: str = Form(...), author_id: str = Form(...), db: Session = Depends(get_db)):
    print(f'Request to get /books/add page received with title:{title}, pages:{pages}')
    db_book = dbs.get_book(db, title=title)
    if db_book:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book already exists.")
    book = schema.CreateBook
    book.title = title
    book.author_id = int(author_id)
    book.pages = int(pages)
    dbs.create_book(db, book=book)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/books/cancel_add", status_code=status.HTTP_200_OK)
def cancel_add(request: Request):
    print(f'Request to get /books/cancel_add page received')
    return templates.TemplateResponse('books/partials/show_add_form.html', {"request": request})


@app.get("/books", status_code=status.HTTP_200_OK)
def get_books(request: Request, db: Session = Depends(get_db)):
    print(f'Request to get /books page received')
    vm = showbooks.ShowBooksViewModel(db=db)
    books = vm.books
    return templates.TemplateResponse('books/books.html', {"request": request, "books": books, "search_text": ""}, status_code=status.HTTP_200_OK)


@app.get("/books/search", status_code=status.HTTP_200_OK)
def search_books(request: Request, search_text: str, db: Session = Depends(get_db)):
    print(f'Request to get /books/search page received with search_text:{search_text}')
    vm = searchbooks.SearchViewModel(db=db, search_text=search_text)
    if request.headers.get('HX-Request'):
        return templates.TemplateResponse("books/partials/search_results.html", {"request": request, "books": vm.books})
    return templates.TemplateResponse('books/books.html', {"request": request, "books": vm.books, "search_text": search_text})
