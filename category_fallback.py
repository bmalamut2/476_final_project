from api_tools import call_model_chat_completions

system_prompt = '''
    We have been unable to solve the given question using either code or a web search. Please use your internal knowledge to answer the question. We will provide both the chat history and the question. Return only the final answer.
'''

def get_fallback_answer(question: str, history: str) -> str:
    response = call_model_chat_completions(
        system = system_prompt,
        prompt = f"Chat History:\n{history}\n\nQuestion:\n{question}"
    )
    return response.get('text', '')
