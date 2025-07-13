from llm import client, json_client
from prompts import get_current_date, query_writer_instructions, summarizer_instructions, answer_instructions, reflection_instructions
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re

def clean_llm_output(text: str) -> str:
    """Removes <think> tags and trims whitespace from the LLM output."""
    if not isinstance(text, str):
        return text
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return text.strip()

def generate_query(query: str, reflection: str = None):
    """Function node that generates a search query based on the research topic."""
    current_date = get_current_date()
    prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=query
    )
    if reflection:
        prompt += f"\n\n<reflection>\n{reflection}\n</reflection>"

    result = client.invoke(
        [SystemMessage(content=prompt),
         HumanMessage(content="Generate a query for web search: /no_think")]
    )
    content = clean_llm_output(result.content)
    
    return {"search_query": content}

def summarize_sources(content: str, query: str):
    """Function that summarizes web research results."""
    # Truncate content to the first 16000 characters
    truncated_content = content[:16000]
    human_message_content = (
        f"<Content_to_summarize> \n {truncated_content} \n </Content_to_summarize> /no_think"
    )
    result = client.invoke(
        [SystemMessage(content=summarizer_instructions.format(user_question=query)),
         HumanMessage(content=human_message_content)]
    )
    summary = clean_llm_output(result.content)
    return {"summary": summary}

def reflect_on_summary(summary: str, query: str):
    """Function that reflects on the summary to identify knowledge gaps."""
    prompt = reflection_instructions.format(research_topic=query, summary=summary)
    result = json_client.invoke(
        [SystemMessage(content=prompt),
         HumanMessage(content="Reflect on the summary and generate a follow-up query:")]
    )
    content = clean_llm_output(result.content)
    reflection = json.loads(content)
    return {"reflection": reflection}

def generate_final_answer(summaries: str, query: str):
    """Generate a high-quality answer to the user's question based on the provided summaries."""
    current_date = get_current_date()
    
   
    
    prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=query,
        summaries=summaries
    )
    result = client.invoke(
        [SystemMessage(content=prompt),
         HumanMessage(content="Generate the final answer:")]
    )
    answer = clean_llm_output(result.content)
    return {"answer": answer}
