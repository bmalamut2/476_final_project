from duckduckgo_search import DDGS

from api_tools import call_model_chat_completions
from category_fallback import get_fallback_answer

search_system_prompt = '''
    You are an expert researching agent. You have access to a search engine. Given a question, you will return a query to search for relevant information. Return only what you want to search.
'''
fallback_search_system_prompt = '''
    You are an expert researching agent. You have access to a search engine. Given a question and an error from a previous search, you will return a corrected query to search for relevant information. Return only what you want to search.
'''
final_system_prompt = '''
    You are an expert researching agent. You will be given a question and results from a search engine to help you answer the question. Use the search results to produce a final answer to the question. Output only the final answer.
'''

def web_search(query: str) -> tuple(bool, str):
    try:
        results = []

        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                search_title = r['title']
                search_snippet = r['snippet']
                results.append(f"Title: {search_title}\nSnippet: {search_snippet}")

        if not results:
            return False, "No results found."

        return True, "\n\n".join(results)

    except Exception as e:
        return False, str(e)

def answer_question(question: str, query: str, result: tuple(bool, str), max_searches = 5) -> str:
    for _ in range(max_searches):

        if not result[0]:
            new_query = call_model_chat_completions(
                prompt = f"Question: {question}\nPrevious Query: {query}\nError: {result[1]}\nProvide a new query to search for relevant information.",
                system = fallback_search_system_prompt
            )
            query = new_query
            result = web_search(query)

        return call_model_chat_completions(
            prompt = f"Question: {question}\nSearch Results:\n{result[1]}\nProvide a final answer to the question based on the search results.",
            system = final_system_prompt
        )

    return get_fallback_answer(question=question, history=result)

def search_question(question: str) -> str:
    query = call_model_chat_completions(
        prompt = f"Question: {question}\nProvide a query to search for relevant information.",
        system = search_system_prompt
    )
    result = web_search(query)

    return answer_question(question=question, query=query, result=result)
