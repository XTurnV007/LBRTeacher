from duckduckgo_search import DDGS

def internet_search(query):
    """Perform an internet search using DuckDuckGo and return the results."""
    ddgs = DDGS()
    results = ddgs.text(query, max_results=5)
    search_results = []
    for result in results:
        search_results.append(f"标题: {result['title']}\n链接: {result['href']}\n描述: {result['body']}\n")
    return '\n'.join(search_results)
