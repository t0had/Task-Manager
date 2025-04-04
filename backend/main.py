from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
import fastapi.encoders
import fastapi.staticfiles
from fastapi.middleware.cors import CORSMiddleware
import fastapi
from bcrypt import *
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database_declaration import *
from sqlalchemy_models import *
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_auth_bearer

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

# массив с разрешенными источниками
origins =[
    "http://localhost:3000"
]

# добавление CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=["Authorization"]
)

# эндпоинт для авторизации, который принимает логин/пароль с формы, проверяет их соответствие формату, проверяет существование пользователя, его пароль, 
# при успешном входе формирует и выдает jwt токен. 
@app.post("/login")
def post(login = fastapi.Form(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"), password = fastapi.Form(min_length=6, max_length=30), db: Session = Depends(get_db)):
    try:
        userExist = db.query(Users).filter(Users.login == login).first()
        if userExist == None:
            return JSONResponse({"error": "this user doesn't exist"}, status_code=404)
        if checkpw(password.encode(), str(userExist.password).encode()):
            user_data = {"user_id": f"{userExist.id}"}
            access_token = create_jwt(user_data, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
            return JSONResponse({"message": "authorization success"},headers={"Authorization": "Bearer "+ access_token})
        else:
            return JSONResponse({"error": "wrong_password!"}, status_code=401)
    except BaseException as e:
        return JSONResponse({"error": e})

# эндпоинт для регистрации, который принимает логин/пароль с формы, проверяет их соответствие формату, проверяет существование пользователя, хеширует пароль, создает пользователя и добавляет в базу данных
# при успешной регистрации формирует и выдает jwt токен
@app.post("/register")
def post(login = fastapi.Form(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"), password = fastapi.Form(min_length=6, max_length=30), db: Session = Depends(get_db)):
    try:
        userExist = db.query(Users).filter(Users.login == login).first()
        if userExist != None:
            return JSONResponse({"error": "this user elready exist"}, status_code=409)
        hashed_password = hashpw(str(password).encode(), gensalt()).decode()
        user = Users(login = login, password = hashed_password)
        db.add(user)
        db.commit()
        user_data = {"user_id": f"{user.id}"}
        access_token = create_jwt(user_data, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
        if access_token == None:
            return JSONResponse({"error": "create token error"}, status_code=409)
        return JSONResponse({"message": "authorization success"}, headers={"Authorization": "Bearer "+ access_token})
    except BaseException as e:
        return JSONResponse({"error": e})

# эндпоинт для получения списка задач. принимает значение фильтра, принимает токен. достает информацию о пользователе из токена,
# создает и отправляет запрос к базе данных, для вывода задач с условием фильтра и определенного пользователя (по инфе из токена).
@app.get("/tasks")
def get(filter_status: str, filter_date: str, token = Depends(get_auth_bearer) ,db: Session = Depends(get_db)):
    try:
        payload = get_jwt(token)
        if payload == None:
            return JSONResponse({"error": "get payload from token error"}, status_code=401)
        
        if filter_date == "":
            if filter_status == "Все":
                tasks = db.query(Tasks).filter(Tasks.user_id == payload["user_id"]).all()
            else:
                tasks = db.query(Tasks).filter(Tasks.user_id == payload["user_id"], Tasks.status == filter_status).all()
        else:
            if filter_status == "Все":
                tasks = db.query(Tasks).filter(Tasks.user_id == payload["user_id"], Tasks.dateOfCreation == filter_date).all()
            else:
                tasks = db.query(Tasks).filter(Tasks.user_id == payload["user_id"], Tasks.status == filter_status, Tasks.dateOfCreation == filter_date).all()

        response = JSONResponse(fastapi.encoders.jsonable_encoder(tasks))
        return response
    except BaseException as e:
        return JSONResponse({"error": e})

# эндпоинт, который принимает запрос на создание задачи. он получает данные для создания задачи из тела запроса, также принимает токен для верификации пользователя.
# создает задачу, подставляя данные из тела запроса в нужные поля конструктора объекта задачи, добавляет эту задачу в базу данных, и сохраняет изменения
@app.post("/tasks")
def post(data = fastapi.Body(),token = Depends(get_auth_bearer), db: Session = Depends(get_db)):
    try:
        if token == None:
            return JSONResponse({"error": "get token error"}, status_code=401)
        payload = get_jwt(token)
        if payload == None:
            return JSONResponse({"error": "get payload from token error"}, status_code=401)
        task = Tasks(title = data["title"], description = data["description"], status = data["status"], user_id = payload["user_id"], dateOfCreation = datetime.date(datetime.now()))
        db.add(task)
        db.commit()
        return JSONResponse({"message": "Задача успешно добавлена!"})
    except BaseException as e:
        return JSONResponse({"error": e})

# эндпоинт, который принимает запрос на изменение задачи. в параметрах запроса передается id задачи. также он принимает тело запроса с данными существующей задачи, и токен.
# ищет эту задачу в бд, подставляет данные из тела запроса в поля найденной задачи, и сохраняет изменения.
@app.put("/tasks/{id}")
def put(id: int, data = fastapi.Body(), token = Depends(get_auth_bearer), db: Session = Depends(get_db)):
    try:
        payload = get_jwt(token)
        if payload == None:
            return JSONResponse({"error": "get payload from token error"}, status_code=401)
        task = db.query(Tasks).filter(Tasks.id == id, Tasks.user_id == payload["user_id"]).first()
        if task == None:
            return JSONResponse({"error": "this task doesn't exist for this user"}, status_code=403)
        task.title = data["title"]
        task.description = data["description"]
        task.status = data["status"]
        db.commit()
        return JSONResponse({"message": "задача успешно изменена!"})
    except BaseException as e:
        return JSONResponse({"error": e})

# эндпоинт, который принимает запрос на удаление задачи. в параметрах запроса передается id задачи. также он принимает токен для верификации.
# ищет эту задачу в бд, удаляет её и подтверждает изменения.
@app.delete("/tasks/{id}")
def delete(id: int, token = Depends(get_auth_bearer), db: Session = Depends(get_db)):
    try:
        payload = get_jwt(token)
        if payload == None:
            return JSONResponse({"error": "get payload from token error"}, status_code=401)
        task = db.query(Tasks).filter(Tasks.id == id, Tasks.user_id == payload["user_id"]).first()
        if task == None:
            return JSONResponse({"error": "this task doesn't exist"}, status_code=404)
        db.delete(task)
        db.commit()
        return JSONResponse({"message": "задача успешно удалена!"})
    except BaseException as e:
        return JSONResponse({"error": e})


# uvicorn.run(app=app, host="0.0.0.0", port=8000)