import urllib.request
import urllib.parse
import json
import re

def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo HTML lite.
    Returns clean, summarised results without needing an API key.
    """
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        # extract snippets using basic regex
        snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
        
        if not snippets:
            return f"No results found for '{query}'."
            
        output = []
        for s in snippets[:4]:
            # Clean HTML tags and entities
            clean_text = re.sub(r'<[^>]+>', '', s).strip()
            clean_text = clean_text.replace('<b>', '').replace('</b>', '')
            output.append(f"- {clean_text}")
            
        return "\n".join(output)

    except Exception as e:
        return f"Search error: {str(e)}"