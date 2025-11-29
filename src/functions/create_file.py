import os
from google.genai import types

def create_file(working_directory:str, filepath: str, content: str=""):
    # gets absolute paths
    abs_path = os.path.abspath(os.path.join(working_directory, filepath))

    # checks if file is actually inside the workingt directory
    if not abs_path.startswith(os.path.abspath(working_directory)):
        return {"error" : "path out side working directory is not allowed"}
    
    # create parent directories if required
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    # create file
    try:
        with open(abs_path, "w") as f:
            f.write(content)
        return {"success": True, "path": filepath}
    except Exception as e:
        return {"error": str(e)}
    
# create schema
create_file_schema = types.FunctionDeclaration(
    name='create_file',
    description='Creates a file inside the working directory. Parent folders are created automatically. Optionally writes content into the file.',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            'working_directory': types.Schema(
                type=types.Type.STRING,
                description="Base working directory. Will be overridden by runtime.",
                nullable=True
            ),
            'filepath': types.Schema(
                type=types.Type.STRING,
                description="Relative path to the file to create.",
                nullable=False
            ),
            'content': types.Schema(
                type=types.Type.STRING,
                description="Optional file content.",
                nullable=True
            )
        },
        required=['filepath']
    )
)