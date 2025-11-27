from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

def scrape_website(url: str, max_pages=50) -> dict:
    """
    crawl internal pages of a website and extract html + css
    returns: dict {page_url: {"html": html_string, "css": combined_css_string}}
    """
    visited = set()
    queue = [url]
    site_map = {}

    while queue and len(visited) < max_pages:
        current_url = queue.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)

        # download html of the page
        try:
            response = requests.get(current_url, timeout=5)
            if response.status_code != 200:
                continue
            html = response.text
        except:
            continue

        # parse html
        soup = BeautifulSoup(html, "html.parser")

        # crawl links and add new internal pages to queue
        for a in soup.find_all("a"):
            href = a.get("href")
            if href:
                full_link = urljoin(current_url, href)
                # only keep internal links
                if url in full_link and full_link not in visited:
                    queue.append(full_link)

        # extract css
        css_collection = []

        # inline styles
        inline_styles = [tag['style'] for tag in soup.find_all(style=True)]
        css_collection.extend(inline_styles)

        # internal <style> blocks
        style_blocks = [style_tag.text for style_tag in soup.find_all('style')]
        css_collection.extend(style_blocks)

        # external css files
        link_tags = soup.find_all('link', rel="stylesheet")
        for link_tag in link_tags:
            css_href = link_tag.get('href')
            if css_href:
                css_url = urljoin(current_url, css_href)
                try:
                    css_response = requests.get(css_url, timeout=5)
                    if css_response.status_code == 200:
                        css_collection.append(css_response.text)
                except:
                    pass

        # merge all css into a single string per page
        combined_css = "\n".join(css_collection)

        # store html + css in site_map
        site_map[current_url] = {"html": html, "css": combined_css}

    return site_map
