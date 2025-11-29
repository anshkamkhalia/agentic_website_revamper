import os
from google.genai import types

def get_files_info(working_directory: str, directory: str=None) -> dict:

    # simple guardrails to keep model from accessing private files
    abs_working_dir = os.path.abspath(working_directory) # get absolute path
    if directory is None:
        directory = working_directory
    abs_directory = os.path.abspath(os.path.join(working_directory, directory) if directory != working_directory else working_directory) # absolute path of directory

    if not abs_directory.startswith(abs_working_dir): # checks the prefix of the working directory matches that of the directory the model is trying to access
        return {'error': f"{directory} is outside current working directory"}
    
    dir_contents = os.listdir(abs_directory) # lists out the contents of the directory

    return_dict = {} # initialize, will be returned

    for content in dir_contents:
        is_dir = os.path.isdir(os.path.join(abs_directory, content)) # True if it is a directory, False if it is something else
        size = os.path.getsize(os.path.join(abs_directory, content)) # gets the file size of the current entry

        # update return value
        return_dict[content] = {
            'is_dir': is_dir,
            'file_size': size
        }

    return return_dict

# schema
get_files_info_schema = types.FunctionDeclaration(
    name='get_files_info',
    description='Lists the contents of a specified directory along with their sizes.',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The base working directory. The function restricts access to files within this directory.",
                nullable=True
            ),
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Optional subdirectory within the working directory to list. If omitted, defaults to the working directory.",
                nullable=True
            )
        },
        required=[]
    )
)
