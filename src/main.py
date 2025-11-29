import os
import sys
from google.genai import types
from google import genai
from dotenv import load_dotenv
import time

# import tools
from functions.web_scraper import scrape_website
from functions.call_functions import execute_function_call

# import schemas
from functions.create_file import create_file_schema
from functions.get_files_info import get_files_info_schema
from functions.read_file_contents import read_file_contents_schema
from functions.write_file import write_file_schema
import random

def api_call_with_retry(client, *args, **kwargs):
    """calls api with a waiting time if limits exhausted"""

    backoff = 1
    max_retries = 10
    retries = 0

    while retries < max_retries:
        try:
            return client.models.generate_content(*args, **kwargs) # generate response
        except Exception as e: 
            if "429" in str(e): # catch 429 error
                wait = backoff + random.random() # increase wait time
                print(f"429 received - waiting {wait:.2f}s...")
                time.sleep(wait) # sleep
                backoff = min(backoff * 4, 60)
            else:
                raise e
            
        retries += 1 # increment

MAX_CHARS_PER_CHUNK = 50000  # keep prompt under gemini 2.0 flash-lite token (1 million lmao) for chunking

# NOTE: time.sleep() is used to reset api limits

def chunk_text(text, max_chars=MAX_CHARS_PER_CHUNK):
    """split a long string into chunks of max_chars each"""
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_chars])
        start += max_chars
    return chunks

def main():

    load_dotenv() # loads .env file

    # loads our api key securely
    # NOTE: all of these are gemini keys
    api_key_1 = os.environ.get("KEY_1") 
    api_key_2 = os.environ.get("KEY_2") 
    
    # 3 and 4 not in use yet (unavailable)
    api_key_3 = os.environ.get("KEY_3") 
    api_key_4 = os.environ.get("KEY_4") 

    url = sys.argv[1]   # grab url
    style = sys.argv[2] # style of new website

    # scrape webpages
    results = scrape_website(url)

    # build page prompts individually
    prompt_chunks = []

    print("chunking")

    chunk_counter = 0

    for page_url, data in results.items():
        page_html = data["html"]
        page_css = data["css"]

        # combine html + css for this page
        page_content = f"URL: {page_url}\nCSS:\n{page_css}\nHTML:\n{page_html}\n"

        # split if too long
        for chunk in chunk_text(page_content):
            chunk_counter += 1
            prompt_chunks.append(
                f"This is a website page of a small business. Redesign it in the following style: {style}.\n"
                "Keep content intact, maintain brand identity, ensure mobile-first responsiveness. "
                "Do not alter content, focus on UI/UX.\n"
                f"{chunk}"
            )
            print(f"chunk {chunk_counter}")

    print("\n\n\n-------------------------\n\n\n")
    
    # NOTE: agent_1 is a model that summarizes contents
    # NOTE: agent_2 is a model that analyzes for flaws in styling

    # create genai client
    client = genai.Client(api_key=api_key_1)

    # create system prompt
    AGENT_1_SYSTEM_PROMPT = (
        f"You are a person who is reading a website, and trying to get as much information as possible, who will look at the following chunks of code (pay attention to HTML), and extract ALL of the content related.\n"
        f"Some examples are: phone numbers, addresses, business plans, locations, descriptions, about us, ANYTHING related to their company/business, etc\n"
        f"GET ALL OF THE IMPORTANT INFORMATION THAT YOU CAN!\n"
        f"Ignore CSS, JS, animations, and layout. Only extract meaningful business content.\n"
        f"Return the derived information in a clean summary, keep it detailed. DO NOT FORGET SPECIFIC INFORMATION AS THIS WILL BE PASSED TO ANOTHER API TO GENERATE A WEBSITE, SO IT MUST RETAIN ALL OF THE CONTENT!\n"
        f"If you are not able to derive any information (like css or js code for example), then just return nothing.\n"
        f"Do not actually change anything yet, simply give a detailed summary!"
    )

    agent1_config = types.GenerateContentConfig(system_instruction=AGENT_1_SYSTEM_PROMPT) # pass sys prompt

    agent1_response = "" # summaries will be appended

    print("getting agent 1 summary")

    chunk_counter = 0

    # gets a summary for each chunk (agent1)
    for chunk in prompt_chunks:
        chunk_counter += 1
        try:
            # generate response
            response = api_call_with_retry(
                client=client,
                contents=[chunk], # prompt
                model='gemini-2.0-flash', # use cheaper model for higher token limits
                config=agent1_config
            )
            agent1_response += f"\n{response.text}\n"
        except Exception as e:
            print(f"exception: {e}")
            return

        print(f"chunk {chunk_counter}")

    print("\n\n\n-------------------------\n\n\n")

    client = genai.Client(api_key=api_key_2)
    
    # create system prompt
    AGENT_2_SYSTEM_PROMPT = (
        f"You are a website reviewer who is tasked with analyzing the styles of this website.\n"
        f"You must be extremely critical, and try to point out as many flaws as possible.\n"
        f"The chose revamped style is: {style}, so tailor feedback to that.\n"
        f"Pay attention to CSS for the most part, but also feel free to analyze JS if it includes something like animations.\n"
        f"Provide BOTH: issues(ex: poor font choice, headings too close, clashing colors, etc, but feel free to be as detailed as possible) and ways to improve (increase spacing, use colors (x,y,z), etc).\n"
        f"Be as clear as possible!"
        f"Do not actually change anything yet, simply give a detailed summary, as well as a JSON-style style guide!"
    )

    agent2_config = types.GenerateContentConfig(system_instruction=AGENT_2_SYSTEM_PROMPT) # pass sys prompt

    agent2_response = "" # summaries will be appended

    print("getting agent 2 summary")

    chunk_counter = 0

    # gets a summary for each chunk (agent2)
    for chunk in prompt_chunks:
        chunk_counter += 1
        try:
            # generate response
            response = api_call_with_retry(
                client=client,
                contents=[chunk], # prompt
                model='gemini-2.0-flash', # use cheaper model for higher token limits
                config=agent2_config
            )
            agent2_response += f"\n{response.text}\n"
        except Exception as e:
            print(f"exception: {e}")
            return
        print(f"chunk {chunk_counter}")

    print("\n\n\n-------------------------\n\n\n")

    time.sleep(300) # wait for TPM and RPM to reset to avoid exhausting limits

    # save to .txt files
    with open("agent1_response.txt", "w") as f:
        f.write(agent1_response)
    
    with open("agent2_response.txt", "w") as f:
        f.write(agent2_response)

    # create agentic website coder

    # create directory containing final info
    os.makedirs("final_product", exist_ok=True)

    # list available functions for the model to use
    agent3_available_functions = types.Tool(
        function_declarations=[
            get_files_info_schema,
            write_file_schema,
            read_file_contents_schema,
            create_file_schema,
        ]
    )

    # create system prompt
    AGENT_3_SYSTEM_PROMPT = (
        f"You are a website developer who is in charge of redesigning a website with the following suggestiongs/requirements/issues that need fixing."
        f"You will not be given the original code, but rather a summary of flaws and important information that the website needs to have."
        f"Write code in HTML, CSS, and JS. Code the website with this style: {style}"
        f"Feel free to make as many files as you need."
        f"You will be bound the hardcoded working directory: final_product."
        f"Here are the functions at your disposal:"
        f"1. get_files_info(working_directory, directory) -> lists directory contents\n"
        f"2. write_file(working_directory, filepath, content) -> writes to a file\n"
        f"3. read_file_contents(working_directory, filepath) -> reads a file\n"
        f"4. create_file(working_directory, filepath, content) -> creates a file\n"
        f"You will receive feedback from an evaluator model and will make changes based on that!"
        f"You will ABSOLUTELY NEED to use these functions if you are to satisfy the objective."
        f"Your first step should definitely be creating files for various pages/scripts/styles."
        f"EXTREMELY IMPORTANT NOTE: TO AVOID OVERWRITING AN EXISTING FILE WITH BLANK TEXT IF NO CHANGES ARE NEEDED, SET content='nothing to add' WORD FOR WORD!"
        f"Do NOT create another final_product directory, it already exists."
        f"Make sure that you write code for ALL webpages in the site, not just one."
    )

    # create config
    agent3_config = types.GenerateContentConfig(system_instruction=AGENT_3_SYSTEM_PROMPT, # pass sys prompt
                                         tools=[agent3_available_functions]) # pass tools
    
    # create website evaluator

    # list available functions for the model to use
    agent4_available_functions = types.Tool(
        function_declarations=[
            get_files_info_schema,
            read_file_contents_schema,
        ]
    )

    # create system prompt
    AGENT_4_SYSTEM_PROMPT = (
        f"You are a website reviewer who must analyze the code for possible flaws or visual mistakes."
        f"Fit this style: {style}"
        f"Code is written in HTML, CSS, AND JS."
        f"You will be bound the hardcoded working directory: final_product."
        f"Here are the functions at your disposal:"
        f"1. get_files_info(working_directory, directory) -> lists directory contents\n"
        f"2. read_file_contents(working_directory, filepath) -> reads a file\n"
        f"Your job is not to actually fix any code, but instead review it and return a summary of things that are good, and things that should be fixed."
        f"When mentioning fixes, if applicable, also say the filename of where the fix should be."
        f"Use these functions to your advantage to read and view files."
    )

    # create config
    agent4_config = types.GenerateContentConfig(system_instruction=AGENT_4_SYSTEM_PROMPT, # pass sys prompt
                                                tools=[agent4_available_functions]) # pass tools

    # agentic loop
    MAX_ITERS = 5

    prev_feedback = None
    global prompt

    # client3 = genai.Client(api_key=api_key_3)
    # client4 = genai.Client(api_key=api_key_4)

    client3 = genai.Client(api_key=api_key_1)
    client4 = genai.Client(api_key=api_key_2)

    print("beginning agent loop...")
    for iteration in range(1, MAX_ITERS+1):
            
        for build in range(0,3):
            # call agent 3 to create website

            if prev_feedback is None: # checks for first iteration
                prompt = f"Generate a website based on this summary with a {style} style. Make sure to include the following content as well as fixes. Create website in the final_product/ working directory. Make sure to create separate .html, .css, and .js files for each page if they are required. Here are your summaries - CONTENT: {agent1_response}\n\n STYLES AND MORE: {agent2_response}"
            else:
                prompt = f"The eval model has said this: {prev_feedback}, now refactor and improve the code to relfect these changes. The code is located in the final_product directory. Check the files agent1_response.txt and agent2_response.txt in the final_product directory (the working directory) to make double check code quality and accuracy to content."

            time.sleep(120)

            # generate response
            response = api_call_with_retry(
                client=client3,
                contents=[prompt], # prompt
                model='gemini-2.5-flash', # use cheaper model for higher token limits
                config=agent3_config,
            )

            # call appropriate functions
            if response.function_calls:
                for call in response.function_calls:
                    result = execute_function_call(call)
                    print(result)
            else:
                print(response.text)

        # call agent 4 to review website

        if prev_feedback is None: # checks for first iteration
            prompt = f"Review the code in the final_product directory, and make suggestions for improvements based on this style: {style}. Check the files agent1_response.txt and agent2_response.txt in the final_product directory (the working directory) to make double check code quality and accuracy to content."
        else:
            prompt = f"The coding agent has updated the code, now review it to see if it has improved. The files will be located in the final_product directory. Check the files agent1_response.txt and agent2_response.txt in the final_product directory (the working directory) to make double check code quality and accuracy to content."
        
        # generate response
        response = api_call_with_retry(
            client=client4,
            contents=[prompt], # prompt
            model='gemini-2.0-flash-lite', # use cheaper model for higher token limits
            config=agent4_config,
        )
        time.sleep(30)

        # call function
        if response.function_calls:
            for call in response.function_calls:
                result = execute_function_call(call)
                print(result)
        else:
            prev_feedback = response.text
            print(response.text)

        print(f"iteration {iteration}")
        time.sleep(120) # reset API limits


if __name__ == "__main__":
    main()
