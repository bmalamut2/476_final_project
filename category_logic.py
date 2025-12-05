import subprocess
import sys

from api_tools import call_model_chat_completions
from category_fallback import get_fallback_answer

system_prompt = '''
    You are an expert Python developer. Write Python code to solve the provided questions. Only return valid Python code, ready to be run.
'''
fallback_system_prompt = '''
    You are an expert Python developer. You will be given a question, code from a previous attempt to solve it, and the error message from that code. Analyze the error message and fix the code accordingly. Only return valid Python code, ready to be run.
'''

def run_python(code: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output = True,
            text = True,
            timeout = 5  
        )

        if result.returncode == 0:
            return (True, result.stdout.strip())
        else:
            return (False, result.stderr.strip())

    except subprocess.TimeoutExpired:
        return (False, "Execution timed out, there is likely an infinite loop")

    except Exception as e:
        return (False, str(e))

def answer_question(result: tuple[bool, str], question: str, code: str, max_calls: int = 5) -> str:
    for _ in range(max_calls):

        if not result[0]:
            new_code_response = call_model_chat_completions(
                prompt = f"Question: {question}\nError: {result[1]}\nPrevious Code:\n{code}\nPlease fix the code to address the error.",
                system = fallback_system_prompt
            )
            code = new_code_response.get('text', '')
            result = run_python(code)
            continue

        return result[1]

    return get_fallback_answer(question=question, history=code)

def logic_question(question: str) -> str:
    code_response = call_model_chat_completions(
        prompt = question,
        system = system_prompt
    )
    code = code_response.get('text', '')
    result = run_python(code)

    return answer_question(result, question, code)
