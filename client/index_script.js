// добавляет к кнопке "выход" обработку события "click".
// при вызове этого события, всплывает окно подтверждения выхода.
// в случае подтверждения удаляет jwt токен из localstorage, и адресует на страницу авторизации/регистрации
document.getElementById("logOut").addEventListener("click", async function (event) {
    var confirmation = confirm("Вы уверены, что хотите выйти?");
    if (confirmation) {
        event.preventDefault();
        localStorage.removeItem("auth_token");
        window.location.href = "/login_register_page";
    }
});

// функция получения данных с задачами, и их размещения на странице.
// сначала она проверяет наличие jwt токена.
// потом отправляет get запрос на получение данных с задачами с бэкэнда
// кодирует полученные данные в json формат.
// и для каждой задачи из полученных данных создает строку на странице, и создает и заполняет необходимые поля в строке информацией о задаче
async function getData() {
    document.getElementById("tasks_table").innerHTML = "";
    var auth_token = localStorage.getItem("auth_token");
    if (auth_token == null) {
        alert("Отсутствует токен! Пожалуйста, авторизуйтесь!");
        window.location.href = "/login_register_page";
        return;
    }
    var taskFilterData = {};
    taskFilterData.filter = document.getElementById("filter_status").value;
    var taskRequest = await fetch(`/tasks?filter=${taskFilterData.filter}`, { method: "GET", headers: { "Authorization": "Bearer " + auth_token } });
    if (taskRequest.ok == false) {
        alert("Недействительный токен! Пожалуйста, авторизуйтесь!");
        window.location.href = "/login_register_page";
        return;
    }
    var JSONResponse = await taskRequest.json();
    for (task of JSONResponse) {
        var row = document.createElement("tr");
        document.getElementById("tasks_table").appendChild(row);
        row.addEventListener("click", function (event) {
            document.getElementById("edit_id").value = this.querySelector(".task_id").textContent;
            document.getElementById("edit_title").value = this.querySelector(".task_title").textContent;
            document.getElementById("edit_description").value = this.querySelector(".task_description").textContent;
            document.getElementById("edit_status").value = this.querySelector(".task_status").textContent;
            document.getElementById("dialog_edit_task").showModal();
        });

        var idCell = document.createElement("td")
        idCell.className = "task_id";
        idCell.textContent = task.id;
        row.appendChild(idCell);

        var titleCell = document.createElement("td")
        titleCell.className = "task_title";
        titleCell.textContent = task.title;
        row.appendChild(titleCell);

        var descriptionCell = document.createElement("td")
        descriptionCell.className = "task_description";
        descriptionCell.textContent = task.description;
        row.appendChild(descriptionCell);

        var statusCell = document.createElement("td")
        statusCell.className = "task_status";
        statusCell.textContent = task.status;
        row.appendChild(statusCell);

        var dateCell = document.createElement("td")
        dateCell.className = "task_dateOfCreation";
        dateCell.textContent = new Date(task.dateOfCreation).toLocaleString();
        row.appendChild(dateCell);
    }
    console.log(JSONResponse);
}
getData();

// при каждом изменении значения фильтра по статусу, вызывает обновление задач
document.getElementById("filter_status").addEventListener("change", async function (event) {
    getData();
})

// добавляет обработку события нажатия на кнопку "добавить задачу", и при вызове этого события показывает окно с формой с полями для добавления задачи
// при вызове события "submit" с формы, делает следующее:
// собирает данные с формы в json объект, кодирует его в строку
// получает токен с localstorage
// отправляет post запрос на бэкэнд, с данными с формы в теле запроса, и токеном в заголовке
document.getElementById("add_task").addEventListener("click", (event) => document.getElementById("dialog_add_task").showModal());
document.getElementById("add_task_form").addEventListener("submit", async function (event) {
    event.preventDefault();
    document.getElementById("dialog_add_task").close();
    var form = new FormData(document.getElementById("add_task_form"));
    var formData = {};
    for (entry of form) {
        formData[entry[0]] = entry[1];
    }
    var formDataJson = JSON.stringify(formData);
    var auth_token = localStorage.getItem("auth_token");
    if (auth_token == null) {
        alert("Отсутствует токен! Пожалуйста, авторизуйтесь!");
        window.location.href = "../login_register_page";
        return;
    }
    var taskPostResponse = await fetch("/tasks", { method: "POST", body: formDataJson, headers: { "Authorization": "Bearer " + auth_token, "Content-Type": "application/json" } });
    if (taskPostResponse.ok == false) {
        alert("Произошла ошибка при добавлении заметки");
    }
    alert("Запрос прошел успешно!");
    getData();
});

// при вызове события "submit" с формы редактирования задачи, делает следующее:
// собирает данные с формы в json объект, кодирует его в строку
// получает токен с localstorage
// отправляет post запрос на бэкэнд, с данными с формы в теле запроса, и токеном в заголовке
document.getElementById("edit_task_form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var taskData = {};
    var taskId = document.getElementById("edit_id").value;
    taskData.title = document.getElementById("edit_title").value;
    taskData.description = document.getElementById("edit_description").value;
    taskData.status = document.getElementById("edit_status").value;
    var auth_token = localStorage.getItem("auth_token");
    if (auth_token == null) {
        alert("Отсутствует токен! Пожалуйста, авторизуйтесь!");
        window.location.href = "../login_register_page";
        return;
    }
    var taskDataJson = JSON.stringify(taskData);
    console.log(taskDataJson);
    var response = await fetch(`/tasks/${taskId}`, { method: "PUT", body: taskDataJson, headers: { "Authorization": "Bearer " + auth_token, "Content-Type": "application/json" } });
    console.log(response);
    if (response.ok == false) {
        alert("Произошла ошибка при изменении задачи!");
        return;
    }
    alert("Задача успешно изменена!");
    document.getElementById("dialog_edit_task").close();
    getData();
});

// добавляет обработку события "click" на кнопке удаления задачи. При вызове этого события делает следующее:
// получает id задачи, берет токен из localstorage.
// отправляет delete запрос, с токеном в заголовке. также в параметрах запроса передается id задачи, которую необходимо удалить.
document.getElementById("dialog_delete_task_button").addEventListener("click", async function (event) {
    var taskId = document.getElementById("edit_id").value;
    var auth_token = localStorage.getItem("auth_token");
    if (auth_token == null) {
        alert("Отсутствует токен! Пожалуйста, авторизуйтесь!");
        window.location.href = "../login_register_page";
        return;
    }
    var response = await fetch(`/tasks/${taskId}`, { method: "DELETE", headers: { "Authorization": "Bearer " + auth_token } });
    if (response.ok == false) {
        alert("Произошла ошибка при удалении задачи!");
        return;
    }
    alert("Задача успешно удалена!");
    document.getElementById("dialog_edit_task").close();
    getData();
});