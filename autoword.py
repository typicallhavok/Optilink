import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

sys_inst = """You are an AI assistant for patients with motor neuron disease to communicate in a conversation.  
Your goal is to generate grammatical and coherent words based on the partial input provided.
The user will most likely request help with their daily tasks, such as eating, drinking, or moving around.
Avoid exaggerations, emojis, or irrelevant information. Use correct punctuation, tense, grammar, and capitalization.
For example, for the input 'Sentence: eat di, the output should be: 'dinner'
For another example, for the input 'Sentence: AC 2 d, the output should be: 'down'
"""

genai.configure(api_key=os.getenv("AI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=sys_inst)
chat = model.start_chat()

def autoCompleteWord(input_sentence, chat):
    prompt = f"""
        Predict the end of this sentence: {input_sentence}
        give me 3 outputs it can be completed, just the complete words
        for eg: if the input is "din", the output should be "dinner\ndining\ndinosaur"
    """
    response = chat.send_message(prompt, stream=True)
    completion = ""
    for chunk in response:
        completion += chunk.text
    # print(completion.split("\n"))
    return completion.split("\n")
    

# while True:
#     half_inp = input("Enter half sentence: ")
#     if (half_inp=="exit"):
#         break
#     autoCompleteWord(half_inp, chat)

        
