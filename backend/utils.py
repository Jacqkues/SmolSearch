from typing import Dict, Any, List, Union
from duckduckgo_search import DDGS
from markdownify import markdownify
import httpx
from urllib.parse import quote

def duckduckgo_search(query: str, max_results: int = 3, fetch_full_page: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search the web using DuckDuckGo and return formatted results.
    
    Uses the DDGS library to perform web searches through DuckDuckGo.
    
    Args:
        query (str): The search query to execute
        max_results (int, optional): Maximum number of results to return. Defaults to 3.
        fetch_full_page (bool, optional): Whether to fetch full page content from result URLs. 
                                         Defaults to False.
    Returns:
        Dict[str, List[Dict[str, Any]]]: Search response containing:
            - results (list): List of search result dictionaries, each containing:
                - title (str): Title of the search result
                - url (str): URL of the search result
                - content (str): Snippet/summary of the content
                - raw_content (str or None): Full page content if fetch_full_page is True,
                                            otherwise same as content
    """
    try:
        with DDGS() as ddgs:
            results = []
            search_results = list(ddgs.text(query, max_results=max_results))
            for r in search_results:
                url = r.get('href')
                title = r.get('title')
                content = r.get('body')
                
                if not all([url, title, content]):
                    print(f"Warning: Incomplete result from DuckDuckGo: {r}")
                    continue

                raw_content = content
                if fetch_full_page:
                    print('try to fetch raw content')
                    raw_content = fetch_content(url)
                
                # Add result to list
                result = {
                    "title": title,
                    "url": url,
                    "content": content,
                    "raw_content": raw_content
                }
                results.append(result)
            
            return {"results": results}
    except Exception as e:
        print(f"Error in DuckDuckGo search: {str(e)}")
        print(f"Full error details: {type(e).__name__}")
        return {"results": []}

class JinaReaderError(Exception):
    """Exception raised when Jina Reader API fails."""
    pass

def fetch_jina_markdown(
    url: str,
    timeout: float = 10.0,
    follow_redirects: bool = True,
) -> str:
    """
    Fetches the content of the given URL via Jina's Reader API and returns Markdown.

    Raises:
        JinaReaderError: On network errors or non-200 responses.
    """
    encoded = quote(url, safe='')
    endpoint = f"https://r.jina.ai/{encoded}" if not url.startswith("r.jina.ai/") else url
    print(endpoint)
    headers = {}

    try:
        with httpx.Client(follow_redirects=follow_redirects, timeout=timeout) as client:
            resp = client.get(endpoint, headers=headers)
    except httpx.RequestError as e:
        raise JinaReaderError(f"Network error: {e!r}") from e

    if resp.status_code != 200:
        raise JinaReaderError(f"HTTP {resp.status_code}: {resp.text[:200]!r}")

    if not resp.text.strip():
        raise JinaReaderError("Empty markdown response.")

    return resp.text

def fetch_raw_markdown(url: str, timeout: float = 10.0) -> str:
    """
    Fetch HTML via HTTP and convert to Markdown.
    Raises httpx.HTTPError on failure.
    """
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return markdownify(resp.text)

def fetch_content(url: str) -> str:
    """
    Tries successively:
      1. fetch_jina_markdown
      2. fetch_raw_markdown
    and, if both fail, returns a descriptive error.
    """
    try:
        return fetch_jina_markdown(url)
    except Exception as e_jina:
        print(f"Jina Reader failed for {url}: {e_jina}. Falling back to raw HTTP fetch.")
        pass

    try:
        return fetch_raw_markdown(url)
    except Exception as e_raw:
        if isinstance(e_raw, httpx.HTTPStatusError):
            code = e_raw.response.status_code
        else:
            code = "UNKNOWN"
        return f"this datasource is not available (error code: {code})"

def deduplicate_and_format_sources(
    search_response: Union[Dict[str, Any], List[Dict[str, Any]]], 
    max_tokens_per_source: int, 
    fetch_full_page: bool = False
) -> str:
    """
    Format and deduplicate search responses from various search APIs.
    
    Takes either a single search response or list of responses from search APIs,
    deduplicates them by URL, and formats them into a structured string.
    
    Args:
        search_response (Union[Dict[str, Any], List[Dict[str, Any]]]): Either:
            - A dict with a 'results' key containing a list of search results
            - A list of dicts, each containing search results
        max_tokens_per_source (int): Maximum number of tokens to include for each source's content
        fetch_full_page (bool, optional): Whether to include the full page content. Defaults to False.
            
    Returns:
        str: Formatted string with deduplicated sources
        
    Raises:
        ValueError: If input is neither a dict with 'results' key nor a list of search results
    """
    print("in dedupicate")

    # Convert input to list of results
    if isinstance(search_response, dict):
        sources_list = search_response['results']
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            if isinstance(response, dict) and 'results' in response:
                sources_list.extend(response['results'])
            else:
                sources_list.extend(response)
    else:
        raise ValueError("Input must be either a dict with 'results' or a list of search results")
    # Deduplicate by URL
    unique_sources = {}
    for source in sources_list:
        if source['url'] not in unique_sources:
            unique_sources[source['url']] = source
    
    # Format output
    formatted_text = "Sources:\n\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source: {source['title']}\n===\n"
        formatted_text += f"URL: {source['url']}\n===\n"
        formatted_text += f"Most relevant content from source: {source['content']}\n===\n"
        if fetch_full_page:

            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4
            # Handle None raw_content
            raw_content = fetch_content(source['url'])
            if raw_content is None:
                raw_content = ''
                print(f"Warning: No raw_content found for source {source['url']}")
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
                
    return formatted_text.strip()