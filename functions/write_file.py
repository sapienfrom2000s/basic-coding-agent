import os


def write_file(working_directory, file_path, content):
  abs_working_dir = os.path.abspath(working_directory)
  abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

  # Check if target path is within working directory
  if not abs_file_path.startswith(abs_working_dir):
    return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

  try:
    os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)

    with open(abs_file_path, "w") as f:
      f.write(content)

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
  except Exception as e:
    return f'Error: Failed to write to "{file_path}": {e}'
