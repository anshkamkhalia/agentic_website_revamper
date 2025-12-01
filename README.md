# Agentic Website Revamper

This project simulates a team of individuals analyzing, reviewingm, and improving a website.

1. **Scrape website contents**
    - A web scraper made with BeautifulSoup and requests dynamically parses the contents of a page, as well the internal page links.
    - Includes HTML, CSS, and JS
    - Data is chunked to avoid excededing token limits

2. **Agent 1**
    - This agent is tasked with analyzing the contents of the website, so **the 3rd agent** can create a website that does not erase the actual purpose
    - Scraped data is fed chunk-by-chunk into **Gemini 2.0 Flash-Lite** 
    - Summaries are saved in text files

3. **Agent 2**
    - This agent is tasked with finding flaws in the style of the website, as well as making suggestions to how it can improve.
    - This report will be sent to **the 3rd agent** to generate a new website.
    - This model also uses **Gemini 2.0 Flash-Lite**
    - Summaries are saved in text files

4. **Agent 3**
    - This model is a coding agent.
    - It is given 4 tools to manipulate files to build a website based on the summaries from **Agent 1** and **Agent 2**.
    - Uses **Gemini 2.5 Flash** for higher code quality.

5. **Agent 4**
    - A evaluator meant to criticize the work of **Agent 3**.
    - Strictly provided tools to view files, not editing.
    - Uses **Gemini 2.0 Flash-Lite** to balance TPM, RPM, and RPD (has lenient rates)

After the first and second agents have compiled their summaries, Agent 3 will make a website, and Agent 4 will evaluate it, provided feedback. Agent 3 will then use this feedback to improve its next iteration. This will repeat a maximum of 5 times, with the coding agent running 4 times at max, and the evaluator running only once.'

## How to use

Python version - 3.11

Run this command to install dependencies:

```zsh
pip install -r reqiurements.txt
```

Run this command to execute the program:

```zsh
python src/main.py "https://website.com" "preferred style"
```

> Note: you will need to provide your own API keys and store them inside a .env file in the src directory

## Final:

The code will most likely be located in the final_product directory, and the main page will almost always be `index.html`.
To easily view the finished website, download the Live Server extension (if on VS Code), or some similar preview.

> WARNING: THIS PROJECT IS STILL UNDER DEVELOPMENT, WITH MANY ISSUES TO WORK OUT (API limits, images extracting, speed, etc)
