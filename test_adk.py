import sys
from google3.labs.language.genai.agents.googlemart.orchestrator import ExecutiveChef
from google.adk.models.gemini import Gemini

chef = ExecutiveChef(Gemini(model="gemini-1.5-flash"))
agent = chef.get_agent()
print("Tools:", agent.tools)
try:
    print("Function declarations:", agent._get_tool_declarations())
except Exception as e:
    print(e)
