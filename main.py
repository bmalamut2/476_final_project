from api_tools import call_model_chat_completions
from category_logic import logic_question
from category_search import search_question

def classify_question(input: str) -> str:
    system_prompt = '''
        Your goal is to classify the input question into one of two categories. The categories are:
        LOGIC: Does the question require calculation, coding, and/or logic solving?
        SEARCH: Does the question require searching for external information on facts or trivia?
        Reply only with "LOGIC" or "SEARCH".
    '''
    return call_model_chat_completions(
        prompt=input,
        system=system_prompt
    )

def main(input: str) -> str:
    category = classify_question(input)

    if 'logic' in category.lower():
        return logic_question(input)
    else:
        return search_question(input)
