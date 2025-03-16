from fastapi.testclient import TestClient
from fastapi import Depends
from core.config import get_auth_bearer
from main import app, get_jwt
import json

client = TestClient(app=app)

def test_create_task_without_token():
    response = client.post("/tasks", json={"title": "task", "description": "some description", "status": "Новая"})
    assert response.status_code == 401

def test_update_task_without_token():
    response = client.put(f"/tasks/{1}", json={"title": "fasfsa", "description": "tjsrfgjt", "status": "Новая"}, headers={"Authorization": "Bearer "})
    assert response.status_code == 401

def test_authorization_with_not_existing_user():
    response = client.post("/login", data={"login": "email@email.com", "password": "123456"})
    assert response.status_code == 404

def test_registration_with_wrong_inputs():
    response = client.post("/register", data={"login": "Userss", "password": "123456"})
    assert response.status_code == 422