"""Executive Chef Orchestrator for GoogleMart with Tools."""

from google.adk.agents import llm_agent
from google.adk.models import base_llm
from google.adk.planners import built_in_planner
from google.genai import types as genai_types

from google3.labs.language.genai.agents.googlemart.sous_chefs import meal_planner, nutritionist, pantry_scout, sommelier

CHEF_INSTRUCTION = """
You are the Executive Chef of GoogleMart, a grocery chain in Australia.
Your goal is to provide an enhanced online shopping experience.
You maintain a warm, professional, and helpful chef persona.
You help users with:
1. Basket Transformation: Suggesting recipes based on cart contents.
2. Healthy Filter: Providing nutritional information and health tips.
3. Complete the Meal: Suggesting pairings and upsells.

Use your Sous-Chefs (tools) to gather information:
- `meal_planner`: Finds recipes based on cart items.
- `nutritionist`: Provides macros and allergen info for a product.
- `pantry_scout`: Checks for staples based on cart items.
- `sommelier`: Suggests pairings for a product.

Always respond in character as a friendly and expert chef.
"""

class ExecutiveChef:
    """Executive Chef Orchestrator Agent."""

    def __init__(self, model: base_llm.BaseLlm):
        self._agent = llm_agent.LlmAgent(
            model=model,
            name="executive_chef",
            description="GoogleMart Executive Chef Orchestrator",
            instruction=CHEF_INSTRUCTION,
            tools=[meal_planner, nutritionist, pantry_scout, sommelier],
            planner=built_in_planner.BuiltInPlanner(
                thinking_config=genai_types.ThinkingConfig(
                    include_thoughts=True,
                )
            ),
        )

    def get_agent(self) -> llm_agent.LlmAgent:
        return self._agent
