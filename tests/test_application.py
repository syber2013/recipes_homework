import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import get_db
from src.main import app
from src.models import Base

# Настройка тестовой базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_recipes.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Переопределение зависимости get_db для использования тестовой БД
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Создание таблиц в тестовой БД
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_create_recipe():
    response = client.post(
        "/recipes",
        json={
            "name": "Test Recipe",
            "cooking_time": 30,
            "ingredients": "ingredient1, ingredient2",
            "description": "Test description",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Recipe"
    assert data["cooking_time"] == 30
    assert data["ingredients"] == "ingredient1, ingredient2"
    assert data["description"] == "Test description"
    assert data["views"] == 0


def test_read_recipes():
    # Создаем пару рецептов для проверки списка
    client.post(
        "/recipes",
        json={
            "name": "Recipe1",
            "cooking_time": 20,
            "ingredients": "ingredient1",
            "description": "desc1",
        },
    )
    client.post(
        "/recipes",
        json={
            "name": "Recipe2",
            "cooking_time": 10,
            "ingredients": "ingredient2",
            "description": "desc2",
        },
    )
    response = client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_read_recipe_and_increment_views():
    # Создаем рецепт
    response = client.post(
        "/recipes",
        json={
            "name": "Recipe3",
            "cooking_time": 15,
            "ingredients": "ingredient3",
            "description": "desc3",
        },
    )
    recipe_id = response.json()["id"]

    # Получаем рецепт и проверяем увеличение просмотров
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["views"] == 1

    # Получаем снова, просмотры должны увеличиться
    response = client.get(f"/recipes/{recipe_id}")
    data = response.json()
    assert data["views"] == 2


def test_read_nonexistent_recipe():
    response = client.get("/recipes/999999")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "Рецепт не найден"


def teardown_module(module):
    # Удаляем тестовую базу после тестов
    if os.path.exists("./test_recipes.db"):
        os.remove("./test_recipes.db")
