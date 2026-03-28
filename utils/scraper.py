import trafilatura

def scrape_url(url: str) -> str:
    """Scrapes a URL and returns the main text body (clean and boiler-plate free)."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""
    
    # Process the HTML
    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    return text if text else ""
