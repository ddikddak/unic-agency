import importlib.util
import os
import json
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class TestToolInput(BaseModel):
    """Input model for the test_tool function."""
    tool_file_path: str
    input_cases: List[str]

class TestToolOutput(BaseModel):
    """Output model for the test_tool function."""
    success: bool
    tool_file_path: str = Field(..., description="The path to the Python file containing the tool function. Use the same recieved after create_tool.")
    results: List[str] = []
    error_messages: List[str] = []


def test_tool(data: TestToolInput) -> TestToolOutput:
    """
    Tests a tool by importing it from a file and running it with a list of input cases provided as JSON strings.
    The tool's output is expected to be serializable to a JSON string.

    Args:
        data (TestToolInput): An object containing:
            tool_file_path (str): The path to the Python file containing the tool function.
            input_cases (List[str]): A list of JSON strings, where each string represents one input case for the tool.
                                      Example: '{"symbol": "AAPL"}'

    Returns:
        TestToolOutput: An object containing the success status, optional tool_file_path,
                        a list of results (as JSON strings), and a list of error messages.
    """

    results = []
    error_messages = []
    # Handle data being potentially a dict or an object
    try:
        if isinstance(data, dict):
            tool_file_path = data.get('tool_file_path')
            input_cases = data.get('input_cases', [])
        else:
            tool_file_path = data.tool_file_path
            input_cases = data.input_cases
        
        if not tool_file_path:
             raise ValueError("'tool_file_path' is missing or empty in the input.")
        if not isinstance(input_cases, list):
            raise ValueError("'input_cases' must be a list.")

    except (AttributeError, ValueError, TypeError) as e:
         # Attempt to return the path if available, otherwise use an empty string
         return TestToolOutput(success=False, tool_file_path=tool_file_path if 'tool_file_path' in locals() else "", error_messages=[f"Error processing input data: {str(e)}"])

    module_name = None # Initialize module_name

    try:
        # Extract module name from file path
        module_name = os.path.splitext(os.path.basename(tool_file_path))[0]

        # Create a module specification
        spec = importlib.util.spec_from_file_location(module_name, tool_file_path)

        if spec is None or spec.loader is None: # Added check for spec.loader
            raise FileNotFoundError(f"Could not find or load module specification for {tool_file_path}")

        # Create a module from the specification
        module = importlib.util.module_from_spec(spec)

        # Load the module
        spec.loader.exec_module(module)

        # Get the tool function from the module (assuming it has the same name as the module)
        tool_function = getattr(module, module_name)

    except FileNotFoundError as e:
        error_messages.append(f"Error loading tool: {str(e)}")
        return TestToolOutput(success=False, tool_file_path=tool_file_path, error_messages=error_messages)
    except ImportError as e:
        error_messages.append(f"Error importing tool (invalid Python code?): {str(e)}")
        return TestToolOutput(success=False, tool_file_path=tool_file_path, error_messages=error_messages)
    except AttributeError:
        error_messages.append(f"Error: Tool function name '{module_name}' does not match the module name.")
        # module_name might be None here if os.path.basename fails, so handle that potential error message issue
        safe_module_name = module_name if module_name else "[unknown, path error?]"
        error_messages.append(f"Error: Tool function name '{safe_module_name}' does not match the module name/file name.")
        return TestToolOutput(success=False, tool_file_path=tool_file_path, error_messages=error_messages)
    except Exception as e:
        error_messages.append(f"Error during tool import/setup: {str(e)}")
        return TestToolOutput(success=False, tool_file_path=tool_file_path, error_messages=error_messages)

    # If import succeeded, proceed with execution
    import_successful = True
    execution_successful = True
    for input_case_str in input_cases:
        try:
            # Parse the input JSON string
            try:
                input_data = json.loads(input_case_str)
            except json.JSONDecodeError as e:
                error_messages.append(f"Error parsing input JSON '{input_case_str}': {str(e)}")
                execution_successful = False
                continue # Skip to next input case

            # Execute the tool function with the parsed input
            output = tool_function(input_data)

            # Serialize the output to a JSON string
            try:
                output_str = json.dumps(output) # Serialize output
                results.append(output_str)
            except TypeError as e:
                 error_messages.append(f"Error serializing output for input '{input_case_str}': Output is not JSON serializable: {str(e)}")
                 execution_successful = False

        except TypeError as e:
            # Handle errors during tool execution (e.g., wrong argument type if tool expects specific model)
            error_messages.append(f"Error executing tool with input derived from '{input_case_str}': Input type mismatch or incorrect arguments: {str(e)}")
            execution_successful = False
        except Exception as e:
            # Handle other potential errors during tool execution
            error_messages.append(f"Error executing tool with input derived from '{input_case_str}': {str(e)}")
            execution_successful = False

    final_success = import_successful and execution_successful
    return TestToolOutput(
        success=final_success,
        tool_file_path=tool_file_path,
        results=results,
        error_messages=error_messages
    )
