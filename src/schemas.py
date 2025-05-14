from pydantic import BaseModel, ConfigDict

class RecipeSchema(BaseModel):
    name: str
    cooking_time: int
    ingredients: str
    description: str

class RecipeViewSchema(BaseModel):
    id: int
    name: str
    views: int
    cooking_time: int
    ingredients: str
    description: str

    model_config = ConfigDict(from_attributes=True)
