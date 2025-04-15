from google.adk.agents import Agent
import os
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from tools.create_tool_tool import create_tool
from tools.test_tool_tool import test_tool
from google.adk.tools import built_in_code_execution
from dotenv import load_dotenv

load_dotenv()


# Read instruction from file
instruction_path = os.path.join(os.path.dirname(__file__), "instructions.md")
with open(instruction_path, "r") as f:
    agent_instruction = str(f.read().strip())

# Define the agent
sub_agent = Agent(
    name="tool_creation_agent",
    model="gemini-2.0-flash",  # Use Gemini model
    description="Agent that creates and manages tools.",
    instruction=agent_instruction,
    tools=[create_tool, test_tool],
) 


if __name__ == "__main__":
    APP_NAME = "stock_app"
    USER_ID = "1234"
    SESSION_ID = "session1234"
    # Session and Runner
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


    # Agent Interaction
    def call_agent(query):
        content = types.Content(role='user', parts=[types.Part(text=query)])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

        for event in events:
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                    print("Agent Response: ", final_response)

    print("Agent is ready. Type 'exit' to quit.")
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        call_agent(user_query)
        