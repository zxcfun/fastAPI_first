from fastapi import FastAPI,HTTPException,Response,Depends,Form
from fastapi.responses import FileResponse
import uvicorn
from pydantic import BaseModel,Field
from authx import AuthX,AuthXConfig
app=FastAPI()
books=[
    {
        "id":0,
        "name":"book1",
        "author":"vasa"
    },
    {
        "id":1,
        "name":"book2",
        "author":"dima"
    }
]
@app.get("/books",tags=["Книги"],summary="Получить все книги")
def read_books():
    return books

@app.get("/books/{book_id}",tags=["Книги"],summary="Получить конкретную книгу")
def get_hook(book_id:int):
    for book in books:
        if book["id"]==book_id:
            return book
    raise HTTPException(status_code=404,detail="Книга не найдена")

class NewBook(BaseModel):
    title: str  = Field(max_length=300)
    author: str = Field(max_length=60)

@app.post("/books",tags=["Книги"])
def create_book(new_book:NewBook):
    books.append({
        "id": len(books),
        "title": new_book.title,
        "author": new_book.author
    })
    return {"success": True,"message":"Книга успешно добавлена","id":len(books)-1}

@app.get("/file")
async def file():
    return FileResponse("templates/index.html", media_type="text/html")

class FormData(BaseModel):
    fio: str
    phone: str
    birthdate: str

@app.post("/submit")
async def submit(data: FormData):
    print("Получено:", data.fio, data.phone, data.birthdate)
    return {"success": True}
#------------------------------------------------------------
config=AuthXConfig()
config.JWT_SECRET_KEY="SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME="my_access_token"
config.JWT_TOKEN_LOCATION=["cookies"]

security = AuthX(config=config)

class UserLoginSchema(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(creds:UserLoginSchema,response:Response):
    if creds.username=="test" and creds.password=="test":
        token= security.create_access_token(uid="12345")
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME,token)
        return {"access_token":token}
    raise HTTPException(status_code=401,detail="Incorrect username or password")

@app.get("/protected",dependencies=[Depends(security.access_token_required)])
async def protected():
    return {"data":"Top Secret"}

if __name__ == "__main__":
    uvicorn.run("main:app",reload=True)