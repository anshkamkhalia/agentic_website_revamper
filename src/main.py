import os
import sys
from functions.web_scraper import scrape_website
from google.genai import types
from google import genai
from dotenv import load_dotenv
import time

MAX_CHARS_PER_CHUNK = 100000  # keep prompt under gemini 2.0 flash-lite token (1 million lmao) for chunking

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
    api_key = os.environ.get("GEMINI_API_KEY") # loads our api key securely

    url = sys.argv[1]   # grab url
    style = sys.argv[2] # style of new website

    # scrape webpages
    results = scrape_website(url)

    # build page prompts individually
    prompt_chunks = []

    for page_url, data in results.items():
        page_html = data["html"]
        page_css = data["css"]

        # combine html + css for this page
        page_content = f"URL: {page_url}\nCSS:\n{page_css}\nHTML:\n{page_html}\n"

        # split if too long
        for chunk in chunk_text(page_content):
            prompt_chunks.append(
                f"This is a website page of a small business. Redesign it in the following style: {style}.\n"
                "Keep content intact, maintain brand identity, ensure mobile-first responsiveness. "
                "Do not alter content, focus on UI/UX.\n"
                f"{chunk}"
            )

    print(len(prompt_chunks))
    
    # NOTE: agent_1 is a model that summarizes contents
    # NOTE: agent_2 is a model that analyzes for flaws in styling

    # create genai client
    client = genai.Client(api_key=api_key)

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

    # gets a summary for each chunk (agent1)
    for chunk in prompt_chunks:
        
        try:
            # generate response
            response = client.models.generate_content(
                contents=[chunk], # prompt
                model='gemini-2.0-flash-lite', # use cheaper model for higher token limits
                config=agent1_config
            )
            agent1_response += f"\n{response.text}\n"
        except Exception as e:
            print(f"exception: {e}")
            return
        
    time.sleep(1000) # wait for TPM and RPM to reset to avoid exhausting limits
        
    # create system prompt
    AGENT_2_SYSTEM_PROMPT = (
        f"You are a website reviewer who is tasked with analyzing the styles of this website.\n"
        f"You must be extremely critical, and try to point out as many flaws as possible.\n"
        f"The chose revamped style is: {style}, so tailor feedback to that.\n"
        f"Pay attention to CSS for the most part, but also feel free to analyze JS if it includes something like animations.\n"
        f"Provide BOTH: issues(ex: poor font choice, headings too close, clashing colors, etc, but feel free to be as detailed as possible) and ways to improve (increase spacing, use colors (x,y,z), etc).\n"
        f"Be as clear as possible!"
        f"Do not actually change anything yet, simply give a detailed summary!"
    )

    agent2_config = types.GenerateContentConfig(system_instruction=AGENT_2_SYSTEM_PROMPT) # pass sys prompt

    agent2_response = "" # summaries will be appended

    # gets a summary for each chunk (agent2)
    for chunk in prompt_chunks:
        
        try:
            # generate response
            response = client.models.generate_content(
                contents=[chunk], # prompt
                model='gemini-2.0-flash-lite', # use cheaper model for higher token limits
                config=agent2_config
            )
            agent2_response += f"\n{response.text}\n"
        except Exception as e:
            print(f"exception: {e}")
            return

    # save to .txt files
    with open("agent1_response.txt", "w") as f:
        f.write(agent1_response)
    
    with open("agent2_response.txt", "w") as f:
        f.write(agent2_response)
    
if __name__ == "__main__":
    main()
