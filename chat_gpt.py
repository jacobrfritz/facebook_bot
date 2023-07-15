import openai, os
from dotenv import load_dotenv

def birthday_message(name,month,day):
    load_dotenv()
    openai.api_key = os.getenv('gpt_key')
    res = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "user", "content": f"""Write a positive but not too personal 
             birthday message to {name}. Their birthday is {str(month)}/{str(day)}. 
             The first sentence will be a cool fact about that date, 
             the second sentence will say happy birthday """},
        ]
    )
    return res.choices[0].message.content
