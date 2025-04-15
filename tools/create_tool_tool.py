import os

def create_tool(tool_name: str, imports: list[str], code: str):
    """Create a new tool with the given name.
    
    Args:
        tool_name: Name of the tool
        code: Actual implementation code of the tool, it must include the imports, name, docstring, and function definition
        imports: List of required imports
        
    Returns:
        Dictionary with creation status and information
    """
    # Create the tool directory if it doesn't exist
    tools_dir = "tools"
    os.makedirs(tools_dir, exist_ok=True)
    
    # Generate the file path
    file_path = os.path.join(tools_dir, f"{tool_name.lower().replace(' ', '_')}.py")
    
    # Generate file content
    content = ""
    
    # Add code implementation
    if code:
        content += code.strip() + "\n"  # Write the code as is
    else:
        # Add placeholder implementation (This part assumes placeholder should be indented)
        content += "    # TODO: Implement tool functionality\n"
        content += "    pass\n"
    
    # Write to file
    with open(file_path, "w") as f:
        f.write(content)
    
    return {
        "status": "success",
        "tool_name": tool_name,
        "file_path": file_path,
        "message": f"Tool '{tool_name}' created successfully and saved to {file_path}"
    }