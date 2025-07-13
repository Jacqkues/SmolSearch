from utils import duckduckgo_search, deduplicate_and_format_sources
from ai_tools import generate_query, summarize_sources, generate_final_answer, reflect_on_summary
from mcp.server.fastmcp import FastMCP
import time
mcp = FastMCP("websearch_tw3")


@mcp.tool()
def run_research_agent(question: str, max_iterations: int = 2,max_retry:int =2):
    """
    This function runs the research agent to answer a given question.

    Args:
        question (str): The user's question.
        max_iterations (int): The number of research iterations to perform.
        max_retry (int): The number of time we perform a new search if the duckduckgo search give nothing

    Returns:
        str: The final answer to the question.
    """
   
    reflection = None
    urls = "\n"
    for i in range(max_iterations):
        print(f"--- Iteration {i+1} ---")

        print("Generating search query...")
        if reflection:
            query_result = {"search_query": reflection['reflection']['follow_up_query']}
        else:
            query_result = generate_query(question)
        search_query = query_result["search_query"]
        print(f"Search Query: {search_query}")

        print("Performing web search...")
        search_results = duckduckgo_search(search_query)
        print("search ok")
        
        results = search_results.get("results", [])
        if len(results) < 1:
            print(f"No results found (iteration {i + 1}).")
            # If we have more iterations left, wait and retry
            if max_retry != 0:
                print(f"Waiting for {2} seconds before retrying...")
                time.sleep(2)
                run_research_agent(question,max_iterations,max_retry-1)
            else:
                # Last attempt, return an answer indicating failure
                return {"answer": f"Aucun résultat trouvé pour la question : '{question}' après {max_iterations} tentatives."}

        print(results)
        for res in results:
            print(res.get('url'))
            urls += res.get('url') + "\n"
        
        formatted_sources = deduplicate_and_format_sources(search_results,1000, True)
        if i < max_iterations - 1:
            print("Reflecting on summary...")
            reflection = reflect_on_summary(formatted_sources, question)
            print(f"Knowledge Gap: {reflection['reflection']['knowledge_gap']}")
            print(f"Follow-up Query: {reflection['reflection']['follow_up_query']}")

    answer = generate_final_answer(formatted_sources, question).get("answer") + urls
    return {"answer":answer}

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')

