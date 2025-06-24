import os
import subprocess


def run_python_file(working_directory, file_path):
  abs_working_dir = os.path.abspath(working_directory)
  abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

  # Check if target path is within working directory
  if not abs_file_path.startswith(abs_working_dir):
    return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

  # Check if file exists
  if not os.path.isfile(abs_file_path):
    return f'Error: File "{file_path}" not found.'

  # Check if file is a Python file
  if not file_path.endswith('.py'):
    return f'Error: "{file_path}" is not a Python file.'

  try:
    # Run the Python file with timeout
    result = subprocess.run(
      ['python3', os.path.basename(abs_file_path)],
      capture_output=True,
      text=True,
      timeout=30,
      cwd=os.path.dirname(abs_file_path)
    )

    # Prepare output parts
    output_parts = []

    # Add stdout if present
    if result.stdout:
      output_parts.append(f"STDOUT:\n{result.stdout.rstrip()}")

    # Add stderr if present
    if result.stderr:
      output_parts.append(f"STDERR:\n{result.stderr.rstrip()}")

    # Add exit code message if non-zero
    if result.returncode != 0:
      output_parts.append(f"Process exited with code {result.returncode}")

    # Return combined output or "No output" message
    if output_parts:
      return "\n\n".join(output_parts)
    else:
      return "No output produced."

  except subprocess.TimeoutExpired:
    return f'Error: executing Python file: Timeout after 30 seconds'
  except Exception as e:
    return f'Error: executing Python file: {e}'
