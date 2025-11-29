import os
from google.genai import types

MAX_CHARS = 20000 # to prevent overusing token limits

def write_file(working_directory: str, filepath: str, content: str) -> str:

    # checks if model passed no content
    if content is None or content.strip() == "":
        return "Skipped empty write"
    
    # security check to see if model passed content
    if content == "nothing to add":
        return "Skipped empty write"

    # gets absolute paths
    abs_working_dir = os.path.abspath(working_directory)
    abs_filepath = os.path.abspath(os.path.join(abs_working_dir, filepath))

    # checks if file is in cwd
    if not abs_filepath.startswith(abs_working_dir):
        return f"error: {filepath} is not a valid file to write to in the working directory"
    
    # checks if given path is actually a file/actually exists
    if not os.path.isfile(abs_filepath):
        return f"error: {filepath} is either not a file or doesn't exist yet"
        
    # write to file
    try:
        with open(abs_filepath, "w") as f:
            f.write(content)
            return f''
    except Exception as e:
        return f"exception {e} occurred when attempting to write to file"

# schema
write_file_schema = types.FunctionDeclaration(
    name='write_file',
    description='Overwrites the previous contents of a specified file with new content',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The base working directory. The function restricts access to files within this directory.",
                nullable=True
            ),
            "filepath": types.Schema(
                type=types.Type.STRING,
                description="Relative filepath to the file that should have its contents overwritten.",
                nullable=False
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content that will be written into the given file."
            )
        },
        required=["filepath", "content"]
    )
)
