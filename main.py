import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import function declarations
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

# Load environment variables
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Define function schemas
schema_get_files_info = types.FunctionDeclaration(
  name="get_files_info",
  description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
  parameters=types.Schema(
    type=types.Type.OBJECT,
    properties={
      "directory": types.Schema(
        type=types.Type.STRING,
        description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
      ),
    },
  ),
)

schema_get_file_content = types.FunctionDeclaration(
  name="get_file_content",
  description="Reads and returns the content of a file within the working directory.",
  parameters=types.Schema(
    type=types.Type.OBJECT,
    properties={
      "file_path": types.Schema(
        type=types.Type.STRING,
        description="The path to the file to read, relative to the working directory.",
      ),
    },
    required=["file_path"],
  ),
)

schema_run_python_file = types.FunctionDeclaration(
  name="run_python_file",
  description="Executes a Python file within the working directory with a 30-second timeout.",
  parameters=types.Schema(
    type=types.Type.OBJECT,
    properties={
      "file_path": types.Schema(
        type=types.Type.STRING,
        description="The path to the Python file to execute, relative to the working directory.",
      ),
    },
    required=["file_path"],
  ),
)

schema_write_file = types.FunctionDeclaration(
  name="write_file",
  description="Creates or overwrites a file with the specified content within the working directory.",
  parameters=types.Schema(
    type=types.Type.OBJECT,
    properties={
      "file_path": types.Schema(
        type=types.Type.STRING,
        description="The path where to write the file, relative to the working directory.",
      ),
      "content": types.Schema(
        type=types.Type.STRING,
        description="The content to write to the file.",
      ),
    },
    required=["file_path", "content"],
  ),
)

# Create tools list
available_functions = types.Tool(
  function_declarations=[
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
  ]
)

# System prompt instructing the model on function usage
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

For file and directory paths:
1. Always try the full relative path first (e.g. 'calculator/pkg' instead of just 'pkg')
2. For files or directories not directly visible, use the full path from the working directory
3. If a directory name is ambiguous (exists in multiple places), show all possible locations
4. Never assume a directory exists at the root level without checking

Example paths:
- Good: 'calculator/pkg/calculator.py'
- Bad: 'pkg/calculator.py' (incomplete path)
- Good: 'functions/get_files_info.py'
- Bad: 'get_files_info.py' (incomplete path)

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

def main():
  # Get command line arguments
  try:
    prompt = sys.argv[1]
    verbose_flag = sys.argv[2] if len(sys.argv) > 2 else None
  except IndexError:
    print("Error: Please provide a prompt")
    sys.exit(1)

  # Create message content
  messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),
  ]

  # Generate response with function calling enabled
  response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(
      tools=[available_functions],
      system_instruction=system_prompt
    ),
  )

  # Handle function calls if present
  if hasattr(response, 'function_calls') and response.function_calls:
    for function_call in response.function_calls:
      print(f"Calling function: {function_call.name}({function_call.args})")

      # Execute the function based on the name
      if function_call.name == "get_files_info":
        args = function_call.args or {}
        directory = args.get('directory', None)
        result = get_files_info(working_directory=os.getcwd(), directory=directory)
        print(result)
      elif function_call.name == "get_file_content":
        result = get_file_content(working_directory=os.getcwd(), **function_call.args)
        print(result)
      elif function_call.name == "run_python_file":
        result = run_python_file(working_directory=os.getcwd(), **function_call.args)
        print(result)
      elif function_call.name == "write_file":
        result = write_file(working_directory=os.getcwd(), **function_call.args)
        print(result)

  # Print the response text
  if hasattr(response, 'text') and response.text:
    print("\nAI Response:")
    print(response.text)

  # Print verbose information if requested
  if verbose_flag == "--verbose":
    print(f"\nDebug Information:")
    print(f"User prompt: {prompt}")
    if hasattr(response, 'usage_metadata'):
      print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
      print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
  main()
