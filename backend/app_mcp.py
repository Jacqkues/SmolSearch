from utils import duckduckgo_search, deduplicate_and_format_sources
from ai_tools import generate_query, summarize_sources, generate_final_answer, reflect_on_summary
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("websearch_tw3")


@mcp.tool()
def run_research_agent(question: str, max_iterations: int = 2):
    """
    This function runs the research agent to answer a given question.

    Args:
        question (str): The user's question.
        max_iterations (int): The number of research iterations to perform.

    Returns:
        str: The final answer to the question.
    """
   
    reflection = None
    for i in range(max_iterations):
        print(f"--- Iteration {i+1} ---")

        print("Generating search query...")
        if reflection:
            query_result = {"search_query":reflection['reflection']['follow_up_query']}
        else:
            query_result = generate_query(question)
        search_query = query_result["search_query"]
        print(f"Search Query: {search_query}")

        # 2. Perform web search
        print("Performing web search...")
        search_results = duckduckgo_search(search_query)
        if len(search_results) < 1:
            return {"message":f"no results found for {question}"}
        
        formatted_sources = deduplicate_and_format_sources(search_results, 1000,True)


        if i < max_iterations - 1:
            print("Reflecting on summary...")
            reflection = reflect_on_summary(formatted_sources, question)
            print(f"Knowledge Gap: {reflection['reflection']['knowledge_gap']}")
            print(f"Follow-up Query: {reflection['reflection']['follow_up_query']}")
    
    answer = generate_final_answer(formatted_sources,question)
    print(answer)
    return answer

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')

