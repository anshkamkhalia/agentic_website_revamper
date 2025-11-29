from functions.create_file import create_file
from functions.get_files_info import get_files_info
from functions.read_file_contents import read_file_contents
from functions.write_file import write_file

WORKING_DIRECTORY = "final_product" # website code will be stored here

# create function map to call functions
FUNCTION_MAP = {
    "create_file": create_file,
    "get_files_info": get_files_info,
    "read_file_contents": read_file_contents,
    "write_file": write_file,
}

def execute_function_call(call):

    """executes the function specified by the agent"""

    function_name = call.name
    function_args = {**call.args}

    # overwrite working_directory to all function calls just in case
    function_args['working_directory'] = WORKING_DIRECTORY

    if function_name in FUNCTION_MAP:
        function_to_call = FUNCTION_MAP[function_name]
        return function_to_call(**function_args)
    
    else:
        return f'function {function_name} not found!'

