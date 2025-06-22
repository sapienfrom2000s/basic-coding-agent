import os
import sys
from dotenv import load_dotenv
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

prompt = None
verbose_flag = None

from google.genai import types

try:
  prompt = sys.argv[1]
  verbose_flag = sys.argv[2]

except IndexError:
  pass

if prompt is None:
  sys.exit(1)

messages = [
  types.Content(role="user", parts=[types.Part(text=prompt)]),
]


response = client.models.generate_content(
  model="gemini-2.0-flash-001",
  contents=messages
)

print(response.text)

if verbose_flag == "--verbose":
  print(f"User prompt: {prompt}")
  print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
  print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
