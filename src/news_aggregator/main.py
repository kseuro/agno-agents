from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.storage.sqlite import SqliteStorage
from pydantic import BaseModel, Field
from dotenv import dotenv_values
from typing import List

environment_config = dotenv_values(".env")

# TODO: Build off of this framework:
# https://github.com/agno-agi/agno/blob/main/cookbook/workflows/hackernews_reporter.py

model_id = "gemini-2.0-flash-lite"
description = "You help first-time bakers find success in the kitchen. When given a recipe request, search for recipes online and extract the key information including ingredients, equipment, instructions, and tips. Always provide complete recipe information."  # noqa
prompt = "Find 3 popular chocolate chip cookie recipe and provide the ingredients, equipment, instructions, and tips."


class Recipe(BaseModel):
    name: str = Field(..., description="The name of the recipe.")
    ingredients: List[str] = Field(
        ..., description="Ingredients required to successfully make what the recipe describes."
    )
    equipment: List[str] = Field(..., description="All of the equipment required to prepare the recipe.")
    instructions: List[str] = Field(..., description="The steps required to prepare the recipe.")
    tips_for_success: List[str] = Field(..., description="Any tips that could help improve the outcome.")


class RecipeCollection(BaseModel):
    recipes: List[Recipe] = Field(..., description="A list of recipes that match the search criteria.")
    total_count: int = Field(..., description="Total number of recipes found.")
    search_query: str = Field(..., description="The original search query used to find these recipes.")


agent = Agent(
    model=Gemini(id=model_id, api_key=environment_config["GEMINI_API_KEY"]),
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    description=description,
    response_model=RecipeCollection,
    storage=SqliteStorage(
        table_name="recipe_data",
        db_file="tmp/recipes.db",
        auto_upgrade_schema=True,
    ),
)

agent.print_response(prompt, stream=True)
