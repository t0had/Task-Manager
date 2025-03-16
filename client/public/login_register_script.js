var backendUrl = "http://localhost:8000";

// функция, которая собирает данные с формы авторизации, отправляет запрос с данными в теле на бэкэнд. если запрос прошел неудачно, возвращает сообщение об ошибке.
// принимает с бэкэнда ответ с токеном в заголовке. помещает его в localstorage, и адресует на главную страницу приложения
async function postLogin(event) {
    event.preventDefault();
    var data = new FormData(document.getElementById("login"));
    var response = await fetch(`${backendUrl}/login`, {method: "POST", body: data});
    if (response.ok == false){
        if (response.status == 401){
            alert("Неверный пароль!");
        }
        if (response.status == 422){
            alert("Неправильный формат почты, или неправильная длина пароля!");
        }
        if (response.status == 404){
            alert("Данного пользователя не существует!");
        }
        return;
    }
    if (response.headers.has("Authorization")){
        var header = response.headers.get("Authorization");
        if (header.startsWith("Bearer")){
            var jwt = header.split(" ")[1];
            localStorage.setItem("auth_token", jwt);
            window.location.href = "/";
        }
        else{
            alert("Ошибка токена1!");
            return;
        }
    }
    else{
        alert("Ошибка токена2!");
        return;
    }
}
document.getElementById("login").addEventListener("submit", postLogin); //добавляет к форме авторизации обработку события submit, которое вызывается при нажатии кнопки. при вызове этого события, вызывается функция postLogin

// функция, которая собирает данные с формы регистрации, отправляет запрос с данными в теле на бэкэнд. если запрос прошел неудачно, возвращает сообщение об ошибке.
// принимает с бэкэнда ответ с токеном в заголовке. помещает его в localstorage, и адресует на главную страницу приложения
async function postRegister(event) {
    event.preventDefault();
    var data = new FormData(document.getElementById("register"));
    var response = await fetch(`${backendUrl}/register`, {method: "POST", body: data});
    if (response.ok == false){
        if (response.status == 401){
            alert("Неправильное имя пользователя или пароль!");
        }
        if (response.status == 422){
            alert("Неправильный формат почты, или неправильная длина пароля!");
        }
        if (response.status == 409){
            alert("Данный пользователь уже существует!");
        }
        return;
    }
    if (response.headers.has("Authorization")){
        var header = response.headers.get("Authorization");
        if (header.startsWith("Bearer")){
            var jwt = header.split(" ")[1];
            localStorage.setItem("auth_token", jwt);
            window.location.href = "/";
        }
        else{
            alert("Ошибка токена!");
            return;
        }
    }
    else{
        alert("Ошибка токена!");
        return;
    }
}
document.getElementById("register").addEventListener("submit", postRegister); //добавляет к форме регистрации обработку события submit, которое вызывается при нажатии кнопки. при вызове этого события, вызывается функция postLogin