import os

def get_files_info(working_directory, directory=None):
  if os.path.isdir(working_directory) is False:
    print(f'Error: "{working_directory}" is not a directory')
    return

  if directory is None:
    print("No guard provided")
    return

  if os.path.isdir(directory) is False:
    print(f'Error: "{directory}" is not a directory')
    return

  working_directory_abs_path = os.path.abspath(working_directory)
  directory_abs_path = os.path.abspath(directory)

  if working_directory_abs_path.startswith(directory_abs_path) is False:
    print(f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    return

  list_files_recursive(working_directory_abs_path)

def list_files_recursive(path):
  for entry in os.listdir(path):
    full_path = os.path.join(path, entry)
    is_dir = os.path.isdir(full_path)

    if is_dir:
      print(f"- {entry}: is_dir=True")
      list_files_recursive(full_path)  # Recurse into the subdirectory
    else:
      size = os.path.getsize(full_path)
      print(f"- {entry}: file_size={size} bytes, is_dir=False")
