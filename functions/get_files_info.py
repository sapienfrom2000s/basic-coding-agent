import os
from typing import List, Optional


def find_directories(working_directory: str, target_dir: str) -> List[str]:
  """
  Find all instances of a directory name within the working directory.

  Args:
    working_directory (str): Base directory to search in
    target_dir (str): Directory name to find

  Returns:
    List[str]: List of relative paths where the directory was found
  """
  matches = []
  for root, dirs, _ in os.walk(working_directory):
    if os.path.basename(root) == target_dir or target_dir in dirs:
      # Get the relative path from working directory
      if os.path.basename(root) == target_dir:
        rel_path = os.path.relpath(root, working_directory)
      else:
        rel_path = os.path.relpath(os.path.join(root, target_dir), working_directory)
      matches.append(rel_path)
  return matches


def get_files_info(working_directory: str, directory: Optional[str] = None) -> str:
  """
  Lists files in the specified directory along with their sizes recursively.

  Args:
    working_directory (str): The base working directory path
    directory (str, optional): Directory to list files from, relative to working directory

  Returns:
    str: Formatted string containing file information or error message
  """
  # Convert working directory to absolute path
  working_directory = os.path.abspath(working_directory)

  # If no directory specified, use working directory
  if directory is None:
    target_dir = working_directory
  else:
    # First try direct path
    direct_path = os.path.abspath(os.path.join(working_directory, directory))

    # If direct path doesn't exist, search for directory
    if not os.path.isdir(direct_path):
      matches = find_directories(working_directory, directory)

      if not matches:
        return f'Error: "{directory}" is not a directory or does not exist'

      if len(matches) > 1:
        # If multiple matches found, list them
        message = [f'Multiple directories named "{directory}" found:']
        for match in matches:
          message.append(f"- {match}")
        message.append("\nPlease specify the full path to the desired directory.")
        return "\n".join(message)

      # If single match found, use it
      directory = matches[0]
      direct_path = os.path.abspath(os.path.join(working_directory, directory))

    target_dir = direct_path

  # Safety check - ensure target is within working directory
  if not target_dir.startswith(working_directory):
    return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

  # Collect file information recursively
  output = []
  for root, dirs, files in os.walk(target_dir):
    # Get relative path for display
    rel_path = os.path.relpath(root, target_dir)
    if rel_path != '.':
      # Add directory entry
      indent = '  ' * (rel_path.count(os.sep))
      output.append(f"{indent}- {os.path.basename(root)}/")
    else:
      indent = ''

    # Add files in current directory
    for file in sorted(files):
      file_path = os.path.join(root, file)
      try:
        size = os.path.getsize(file_path)
        size_str = format_size(size)
        output.append(f"{indent}  - {file} ({size_str})")
      except OSError as e:
        output.append(f"{indent}  - {file} (error reading size: {e})")

  # Return empty message if no files found
  if not output:
    return "Directory is empty"

  # Add header with target directory path
  header = f"Contents of {directory or working_directory}:"
  output.insert(0, header)

  # Return formatted list
  return "\n".join(output)


def format_size(size: int) -> str:
  """
  Format file size in human-readable format.

  Args:
    size (int): Size in bytes

  Returns:
    str: Formatted size string
  """
  for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
    if size < 1024:
      if unit == 'B':
        return f"{size} {unit}"
      return f"{size:.1f} {unit}"
    size /= 1024
  return f"{size:.1f} PB"
