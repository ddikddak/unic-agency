from tools_agents.agent import tool_creation_agent

# Example of creating a simple tool
try:
    # For demonstration, we'll print the agent's properties
    print(f"Agent name: {tool_creation_agent.name}")
    print(f"Agent description: {tool_creation_agent.description}")
    print(f"Available tools: {[tool.__name__ for tool in tool_creation_agent.tools]}")
    
    # Example tool creation parameters
    tool_params = {
        "tool_name": "calculator",
        "description": "A simple calculator tool that can perform basic arithmetic operations",
        "inputs": [
            {"name": "operation", "type": "str", "description": "The operation to perform (add, subtract, multiply, divide)"},
            {"name": "a", "type": "float", "description": "First number"},
            {"name": "b", "type": "float", "description": "Second number"}
        ],
        "code": """if operation == "add":
    return a + b
elif operation == "subtract":
    return a - b
elif operation == "multiply":
    return a * b
elif operation == "divide":
    if b == 0:
        return "Error: Division by zero"
    return a / b
else:
    return "Error: Invalid operation" """,
        "imports": ["import math"]
    }
    
    # Directly call the create_tool function
    from tools_agents.agent import create_tool
    
    result = create_tool(**tool_params)
    print("\nTool Creation Result:")
    print(result)
    
except Exception as e:
    print(f"Error: {e}")
    
    # Print available methods and attributes for debugging
    print("\nAvailable methods and attributes on the agent:")
    for attr in dir(tool_creation_agent):
        if not attr.startswith('_'):  # Skip private attributes
            print(f"- {attr}")

# To use the agent interactively
def chat_with_agent():
    print("Chat with the tool creation agent (type 'exit' to quit)")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
            
        response = tool_creation_agent.run(message=user_input)
        print(f"Agent: {response}")

# Uncomment to run the chat interface
# chat_with_agent() 