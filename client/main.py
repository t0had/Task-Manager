from fastapi import FastAPI
from fastapi.responses import FileResponse
import fastapi.staticfiles
import fastapi

app = FastAPI()

app.mount("/public", fastapi.staticfiles.StaticFiles(directory="public"), name="static")

# эндпоинт гет, который принимает запрос на получение страницы приложения. ну и соответственно приняв его, возвращает файл этой страницы клиенту
@app.get("/")
def get():
    return FileResponse("public/index.html")

# эндпоинт, который принимает запрос на получение страницы авторизации
@app.get("/login_register_page")
def get():
    return FileResponse("public/login_register_page.html")

# uvicorn.run(app=app, host="0.0.0.0", port=3000)