import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

sys_inst = """You are an AI assistant for patients with motor neuron disease to communicate in a conversation.  
Your goal is to generate grammatical and coherent sentences based on the partial input provided.
The user will most likely request help with their daily tasks, such as eating, drinking, or moving around.
Some sentences might not be related to the previous context. You should determine the context and generate a sentence that is coherent with the current input only.
Avoid repeating the same sentence.
Avoid connecting unrelated inputs. For example, if the user says 'water' and then 'washroom,' do not assume they are related unless explicitly stated.
Avoid exaggerations, emojis, or irrelevant information. Use correct punctuation, tense, grammar, and capitalization.
For example, for the input 'Keywords: chicken, Context: What do you want to eat for dinner', the output should be: 'I want to eat chicken for dinner.'
For another example, for the input 'Keywords: hot, AC, two. Context: is the room temperature ok', the output should be: 'I am hot, can you turn the AC down by two degrees?'
"""

genai.configure(api_key=os.getenv("AI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=sys_inst)

def is_unrelated(input_text, previous_context, model):
    """
    Ask Gemini whether the current input is unrelated to the previous context.
    """
    if not previous_context:
        return False
    
    prompt = f"""
    Determine if the following input is unrelated to the previous context.
    Previous context: "{previous_context}"
    Current input: "{input_text}"
    Answer with "yes" if the input is unrelated, or "no" if it is related.
    """
    
    response = model.generate_content(prompt)
    answer = response.text.strip().lower()
    
    return answer == "yes"

def autocomplete_sentence(input_text, chat):
    prompt = f"""
    Predict the end of this sentence: {input_text}
    Examples:
    - Input: 'chicken' -> Output: 'I want to eat chicken for dinner.'
    - Input: 'I am hot' -> Output: 'I am hot, can you turn the AC down by two degrees?'
    """
    
    response = chat.send_message(prompt, stream=True)
    completion = ""
    for chunk in response:
        completion += chunk.text

    print(f"\nAutocomplete: {completion}")
    
    print("")
    return completion


# print("Start typing your sentence (type 'exit' to stop):")
chat = model.start_chat()
input_text = ""
previous_context = ""

# while True:
#     word = input("> ")
    
#     if word.lower() == "exit":
#         print("Exiting autocomplete...")
#         break
    
#     if is_unrelated(word, previous_context, model):
#         input_text = word
#     else:
#         input_text += " " + word
#     input_text = input_text.strip()
    
#     previous_context = input_text
#     out = autocomplete_sentence(previous_context, chat)





