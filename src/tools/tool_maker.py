import json
import os
from typing import List, Optional, Dict, Any

class ToolManager:
    """Manages the creation and storage of tools with Python file generation."""
    
    def __init__(self, storage_path: str = "tools_data.json", tools_dir: str = "src/generated_tools"):
        self.storage_path = storage_path
        self.tools_dir = tools_dir
        os.makedirs(self.tools_dir, exist_ok=True)
        self._load_tools()
    
    def _load_tools(self):
        """Load existing tools from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.tools = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.tools = []
        else:
            self.tools = []
    
    def _save_tools(self):
        """Save tools to storage."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.tools, f, indent=2)
    
    def _generate_tool_file(self, tool: Dict[str, Any]) -> str:
        """Generate a Python file for the tool."""
        file_name = f"{tool['name'].lower().replace(' ', '_')}.py"
        file_path = os.path.join(self.tools_dir, file_name)
        
        # Format inputs as function parameters
        params = []
        if tool.get('inputs'):
            for input_param in tool['inputs']:
                param_str = f"{input_param['name']}: {input_param.get('type', 'Any')}"
                if input_param.get('default'):
                    param_str += f" = {input_param['default']}"
                params.append(param_str)
        
        params_str = ", ".join(params)
        
        # Determine return type annotation
        return_type = tool.get('return_type', 'Dict[str, Any]')
        
        # Format the file content
        file_content = f"""# {tool['name']} - {tool['description']}
# Auto-generated tool

{tool.get('imports', '# No specific imports')}

def {tool['name'].lower().replace(' ', '_')}({params_str}) -> {return_type}:
    \"\"\"
    {tool['description']}
    
    {tool.get('docstring', '')}
    \"\"\"
    {tool.get('code', '    # Tool implementation not provided\n    return {"status": "success", "message": "Tool executed"}')}\n
"""
        
        # Write the file
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        return file_path
    
    def create_tool(self, 
                   name: str, 
                   description: str, 
                   inputs: Optional[List[Dict[str, Any]]] = None,
                   code: Optional[str] = None,
                   imports: Optional[str] = None,
                   docstring: Optional[str] = None,
                   return_type: str = "Dict[str, Any]") -> dict:
        """
        Create a new tool with the given specifications and generate a Python file.
        
        Args:
            name: The name of the tool
            description: Brief description of what the tool does
            inputs: List of input parameters with name, type, and optional default value
            code: The Python code implementation of the tool
            imports: Import statements needed for the tool
            docstring: Additional documentation for the tool
            return_type: Return type annotation for the tool
        """
        if not name or not description:
            return {
                "status": "error",
                "message": "Tool name and description are required."
            }
        
        # Check if tool already exists
        if any(tool['name'] == name for tool in self.tools):
            return {
                "status": "error",
                "message": f"Tool '{name}' already exists."
            }
        
        # Create new tool
        new_tool = {
            "name": name,
            "description": description,
            "inputs": inputs or [],
            "code": code,
            "imports": imports,
            "docstring": docstring,
            "return_type": return_type,
            "file_path": ""  # Will be set after file generation
        }
        
        # Generate the Python file
        try:
            file_path = self._generate_tool_file(new_tool)
            new_tool["file_path"] = file_path
            
            self.tools.append(new_tool)
            self._save_tools()
            
            return {
                "status": "success",
                "tool": new_tool,
                "message": f"Tool '{name}' created successfully. Python file generated at {file_path}."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create tool: {str(e)}"
            }
    
    def list_tools(self) -> dict:
        """List all available tools."""
        return {
            "status": "success",
            "tools": self.tools,
            "count": len(self.tools),
            "message": f"Found {len(self.tools)} tools."
        }
    
    def get_tool(self, name: str) -> dict:
        """Get a specific tool by name."""
        tool = next((t for t in self.tools if t['name'] == name), None)
        
        if tool:
            return {
                "status": "success",
                "tool": tool,
                "message": f"Tool '{name}' found."
            }
        else:
            return {
                "status": "error",
                "message": f"Tool '{name}' not found."
            }
    
    def delete_tool(self, name: str) -> dict:
        """Delete a tool by name and its Python file."""
        tool = next((t for t in self.tools if t['name'] == name), None)
        
        if tool and os.path.exists(tool.get('file_path', '')):
            try:
                os.remove(tool['file_path'])
            except OSError:
                pass  # Ignore file deletion errors
        
        initial_count = len(self.tools)
        self.tools = [t for t in self.tools if t['name'] != name]
        
        if len(self.tools) < initial_count:
            self._save_tools()
            return {
                "status": "success",
                "message": f"Tool '{name}' deleted successfully."
            }
        else:
            return {
                "status": "error",
                "message": f"Tool '{name}' not found."
            } 