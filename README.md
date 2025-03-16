## Веб приложение для управления задачами
---
#### Стек технологий
- Backend: язык Python, фреймворк FastAPI, модели ORM SQLAlchemy;
- База данных: Postgresql;
- Fronend: HTML, стили CSS, скрипты на JavaScript

## Описание приложения
---
Данное приложение предназначено для ведения списка дел. Оно позволяет создавать задачи, задавать им заголовок, описание и статус.
## Функционал приложения
---
- Авторизация пользователя
- Регистрация пользователя
- Отображение всех задач на главной странице
- Добавление задачи
- Редактирование задачи
- Удаление задачи
## Как запустить проект
---
1. Установить Docker на ОС, если его ещё нет. И запустить его.
2. Клонировать данный репозиторий
3. Зайти в корневую папку проекта с командной строки
4. Запустить команду `docker compose up -d --build`
5. Зайти в браузер по адресу `localhost:3000`
## Краткая документация API
---
### Endpoints:
---
### Frontend:
1. @app.get("/")
- **Описание:**
	Возвращает главную страницу.
- **Параметры:**
	Отсутствуют.
2. @app.get("/login_register_page")
- **Описание:**
	Возвращает страницу регистрации.
- **Параметры:**
	Отсутствуют.	

---
### Backend:
1. @app.post("/login")
- **Описание:**  
    Аутентификация пользователя по логину и паролю. Проверяет существование пользователя, его пароль и при успешной авторизации выдает JWT-токен.
- **Параметры:**
    - `login` (строка, формат email) – логин пользователя.
    - `password` (строка, 6-30 символов) – пароль пользователя.
- **Зависимости:**
    - `db: Session = Depends(get_db)` – подключение к базе данных.
2. @app.post("/register")
- **Описание:**  
    Регистрация нового пользователя. Проверяет корректность логина, хеширует пароль, сохраняет пользователя в базе и возвращает JWT-токен.
- **Параметры:**
    - `login` (строка, формат email) – логин нового пользователя.
    - `password` (строка, 6-30 символов) – пароль нового пользователя.
- **Зависимости:**
    - `db: Session = Depends(get_db)` – подключение к базе данных.
3. @app.get("/tasks")
- **Описание:**  
    Получение списка задач пользователя. Использует токен для идентификации пользователя и фильтры для выборки задач.
- **Параметры:**
    - `filter_status` (строка) – фильтр по статусу задачи (может быть "Все").
    - `filter_date` (строка) – фильтр по дате создания задачи.
- **Зависимости:**
    - `token = Depends(get_auth_bearer)` – получение JWT-токена, и вырезание из заголовка "authorization" элемента "Bearer" с помощью get_auth_bearer.
    - `db: Session = Depends(get_db)` – подключение к базе данных.
4. @app.post("/tasks")
- **Описание:**  
    Создание новой задачи. Берет данные задачи из тела запроса, а ID пользователя из JWT-токена.
- **Параметры:**
    - `data` (JSON) – содержит `title`, `description`, `status`.
- **Зависимости:**
    - `token = Depends(get_auth_bearer)` – получение JWT-токена, и вырезание из заголовка "authorization" элемента "Bearer" с помощью get_auth_bearer.
    - `db: Session = Depends(get_db)` – подключение к базе данных.
5. @app.put("/tasks/{id}")
- **Описание:**  
    Обновление существующей задачи. Использует ID задачи из URL и обновляет ее данные.
- **Параметры:**
    - `id` (int) – идентификатор задачи.
    - `data` (JSON) – обновленные `title`, `description`, `status`.
- **Зависимости:**
    - `token = Depends(get_auth_bearer)` – получение JWT-токена, и вырезание из заголовка "authorization" элемента "Bearer" с помощью get_auth_bearer.
    - `db: Session = Depends(get_db)` – подключение к базе данных.
6. @app.delete("/tasks/{id}")
- **Описание:**  
	Удаление задачи по ID. Использует токен для проверки прав пользователя.
- **Параметры:**
    - `id` (int) – идентификатор задачи.
- **Зависимости:**
    - `token = Depends(get_auth_bearer)` – получение JWT-токена, и вырезание из заголовка "authorization" элемента "Bearer" с помощью get_auth_bearer.
    - `db: Session = Depends(get_db)` – подключение к базе данных.

## Тестирование
---
Добавлен файл с тестами test_unit.py в папке backend. При его запуске все тесты выполняются успешно.