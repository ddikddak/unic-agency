import os
import subprocess
import sys
import re # Added for parsing imports

def create_tool(tool_name: str, imports: list[str], code: str):
    """Create a new tool with the given name and install required dependencies.
    
    Args:
        tool_name: Name of the tool
        code: Actual implementation code of the tool, it must include the imports, name, docstring, and function definition
        imports: List of required import strings (e.g., "import requests", "from pydantic import BaseModel"). The function will attempt to install the base package (e.g., 'requests', 'pydantic').
        
    Returns:
        Dictionary with creation status and information. If dependency installation fails, status will be 'error'.
    """
    # Create the tool directory if it doesn't exist
    tools_dir = "tools"
    os.makedirs(tools_dir, exist_ok=True)
    
    # --- Dependency Installation ---
    installed_packages = set()
    failed_packages = []

    for imp_str in imports:
        # Basic parsing to extract potential package name
        match = re.match(r"^(?:import|from)\s+([a-zA-Z0-9_]+)", imp_str.strip())
        if match:
            package_name = match.group(1)
            if package_name not in installed_packages:
                print(f"Attempting to install dependency: {package_name}...")
                try:
                    # Use sys.executable to ensure pip from the correct env is used
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", package_name],
                        check=True,  # Raise CalledProcessError on failure
                        capture_output=True,
                        text=True
                    )
                    print(f"Successfully installed {package_name}.")
                    print(result.stdout)
                    installed_packages.add(package_name)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install {package_name}.")
                    print(f"Error: {e}")
                    print(f"Stderr: {e.stderr}")
                    failed_packages.append(package_name)
                except Exception as e:
                    print(f"An unexpected error occurred while trying to install {package_name}: {e}")
                    failed_packages.append(package_name) # Also count unexpected errors as failures

    if failed_packages:
        return {
            "status": "error",
            "tool_name": tool_name,
            "message": f"Failed to install dependencies: {', '.join(failed_packages)}. Tool file not created.",
            "failed_dependencies": failed_packages
        }
    # --- End Dependency Installation ---

    # Generate the file path
    file_path = os.path.join(tools_dir, f"{tool_name.lower().replace(' ', '_')}.py")
    
    # Generate file content
    content = ""
    
    # Add code implementation
    if code:
        content += code.strip() + "\n"  # Write the code as is
    else:
        # Add placeholder implementation (This part assumes placeholder should be indented)
        placeholder_func_name = tool_name.lower().replace(' ', '_')
        content += f"def {placeholder_func_name}():\n" # Basic function definition
        content += "    # TODO: Implement tool functionality\n"
        content += "    pass\n"
    
    # Write to file
    with open(file_path, "w") as f:
        f.write(content)
    
    return {
        "status": "success",
        "tool_name": tool_name,
        "file_path": file_path,
        "message": f"Tool '{tool_name}' created successfully and saved to {file_path}. Required dependencies installed."
    }