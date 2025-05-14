from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Recipe
from schemas import RecipeSchema, RecipeViewSchema

app = FastAPI()

# GET /recipes — получить список всех рецептов
@app.get("/recipes", response_model=List[RecipeViewSchema])
def read_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).order_by(Recipe.views.desc(), Recipe.cooking_time.asc()).all()
    return recipes

# GET /recipes/{recipe_id} — получить детальную информацию о конкретном рецепте
@app.get("/recipes/{recipe_id}", response_model=RecipeViewSchema)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe:
        recipe.views += 1
        db.commit()
        return recipe
    else:
        return {"error": "Рецепт не найден"}

# POST /recipes — создать новый рецепт
@app.post("/recipes", response_model=RecipeViewSchema)
def create_recipe(recipe: RecipeSchema, db: Session = Depends(get_db)):
    db_recipe = Recipe(
        name=recipe.name,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        description=recipe.description,
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe
