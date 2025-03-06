from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, JSONResponse
import fastapi
from bcrypt import *
import fastapi.encoders
import fastapi.staticfiles
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import *
from .models import *
from .core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_auth_bearer

# функция для создания сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# функция для создания jwt токена. она принимает данные с заголовками и информацией о пользователе и временем действия токена
# кодирует это в опр. формат, а также создает подпись с использованием ключа и опр. алгоритма.
def create_jwt(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
# функция для получения информации о пользователе из токена, а также для проверки валидности (правильности) ключа
def get_jwt(token):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except jwt.PyJWTError:
        return None

# инициализация приложения fastapi
app = FastAPI()

app.mount("/client", fastapi.staticfiles.StaticFiles(directory="client"), name="static")

# эндпоинт гет, который принимает запрос на получение страницы приложения. ну и соответственно приняв его, возвращает файл этой страницы клиенту
@app.get("/")
def get():
    return FileResponse("client/index.html")

# эндпоинт, который принимает запрос на получение страницы авторизации
@app.get("/login_register_page")
def get():
    return FileResponse("client/login_register_page.html")

# эндпоинт для авторизации, который принимает логин/пароль с формы, проверяет их соответствие формату, проверяет существование пользователя, его пароль, 
# при успешном входе формирует и выдает jwt токен. 
@app.post("/login")
def post(login = fastapi.Form(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"), password = fastapi.Form(min_length=6, max_length=30), db: Session = Depends(get_db)):
    userExist = db.query(Users).filter(Users.login == login).first()
    if userExist == None:
        return JSONResponse({"error": "this user doesn't exist"}, status_code=404)
    if checkpw(password.encode(), str(userExist.password).encode()):
        user_data = {"user_id": f"{userExist.id}"}
        access_token = create_jwt(user_data, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
        return JSONResponse({"message": "authorization success"},headers={"Authorization": "Bearer "+ access_token})
    return JSONResponse({"error": "wrong_password!"}, status_code=401)

# эндпоинт для регистрации, который принимает логин/пароль с формы, проверяет их соответствие формату, проверяет существование пользователя, хеширует пароль, создает пользователя и добавляет в базу данных
# при успешной регистрации формирует и выдает jwt токен
@app.post("/register")
def post(login = fastapi.Form(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"), password = fastapi.Form(min_length=6, max_length=30), db: Session = Depends(get_db)):
    userExist = db.query(Users).filter(Users.login == login).first()
    if userExist != None:
        return JSONResponse({"error": "this user elready exist"}, status_code=404)
    hashed_password = hashpw(str(password).encode(), gensalt()).decode()
    user = Users(login = login, password = hashed_password)
    db.add(user)
    db.commit()
    user_data = {"user_id": f"{user.id}"}
    access_token = create_jwt(user_data, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    if access_token == None:
        return JSONResponse({"error": "create token error"}, status_code=409)
    return JSONResponse({"message": "authorization success"}, headers={"Authorization": "Bearer "+ access_token})

# эндпоинт для получения списка задач. принимает значение фильтра, принимает токен. достает информацию о пользователе из токена,
# создает и отправляет запрос к базе данных, для вывода задач с условием фильтра и определенного пользователя (по инфе из токена).
@app.get("/tasks")
def get(filter: str, token = Depends(get_auth_bearer) ,db: Session = Depends(get_db)):
    payload = get_jwt(token)
    if payload == None:
        return JSONResponse({"error": "get payload from token error"}, status_code=402)
    if filter == "Все":
        tasks = db.query(Tasks).filter(Tasks.user_id == payload["user_id"]).all()
    else:
        tasks = db.query(Tasks).filter(Tasks.user_id == payload["user_id"], Tasks.status == filter).all()
    response = JSONResponse(fastapi.encoders.jsonable_encoder(tasks))
    return response

# эндпоинт, который принимает запрос на создание задачи. он получает данные для создания задачи из тела запроса, также принимает токен для верификации пользователя.
# создает задачу, подставляя данные из тела запроса в нужные поля конструктора объекта задачи, добавляет эту задачу в базу данных, и сохраняет изменения
@app.post("/tasks")
def post(data = fastapi.Body(),token = Depends(get_auth_bearer), db: Session = Depends(get_db)):
    payload = get_jwt(token)
    if payload == None:
        return JSONResponse({"error": "get payload from token error"}, status_code=402)
    task = Tasks(title = data["title"], description = data["description"], status = data["status"], user_id = payload["user_id"], dateOfCreation = datetime.now().replace(microsecond=0))
    db.add(task)
    db.commit()
    return {"message": "Задача успешно добавлена!"}

# эндпоинт, который принимает запрос на изменение задачи. в параметрах запроса передается id задачи. также он принимает тело запроса с данными существующей задачи, и токен.
# ищет эту задачу в бд, подставляет данные из тела запроса в поля найденной задачи, и сохраняет изменения.
@app.put("/tasks/{id}")
def put(id: int, data = fastapi.Body(),token = Depends(get_auth_bearer), db: Session = Depends(get_db)):
    payload = get_jwt(token)
    if payload == None:
        return JSONResponse({"error": "get payload from token error"}, status_code=402)
    task = db.query(Tasks).filter(Tasks.id == id, Tasks.user_id == payload["user_id"]).first()
    if task == None:
        return JSONResponse({"error": "this task doesn't exist"}, status_code=404)
    task.title = data["title"]
    task.description = data["description"]
    task.status = data["status"]
    db.commit()
    return {"message": "задача успешно изменена!"}

# эндпоинт, который принимает запрос на удаление задачи. в параметрах запроса передается id задачи. также он принимает токен для верификации.
# ищет эту задачу в бд, удаляет её и подтверждает изменения.
@app.delete("/tasks/{id}")
def delete(id: int, token = Depends(get_auth_bearer), db: Session = Depends(get_db)):
    payload = get_jwt(token)
    if payload == None:
        return JSONResponse({"error": "get payload from token error"}, status_code=402)
    task = db.query(Tasks).filter(Tasks.id == id, Tasks.user_id == payload["user_id"]).first()
    if task == None:
        return JSONResponse({"error": "get payload from token error"}, status_code=404)
    db.delete(task)
    db.commit()
    return {"message": "задача успешно удалена!"}
