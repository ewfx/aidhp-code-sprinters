import os
import httpx
import openai
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai

def call_openai_service(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content.strip()    
        return result
    except Exception as e:
        raise Exception(f"OpenAI translation failed: {str(e)}")

def get_openai_reasoning(profile):
    system_prompt = f"""You are an intelligent reasoning assistant helping summarising user profile".  
    Your task is to analyze the user profile and create linguitic constructs as described below.
    Template: [User Profile], interested in [Financial Goal], specifically through [Key Features] to achieve [Desired Outcome] with [Additional Benefits]. 
    construct sample: A salaried employee in the IT industry, aged 25-34, is actively looking to purchase their first home. They are interested in a long-term mortgage with flexible repayment options, prioritizing low EMI and tax benefits to ensure financial ease in homeownership.
    Above example is for reference only.
    Output the construct in json format with key as "construct"
    """

    user_prompt=f"""User profile "{profile}". Do not add additional content in the respone. Provide only json output.
    **Output Format (JSON):**  
    {{
    "construct": "value goes here"
    }}  
    """
    result = call_openai_service(system_prompt, user_prompt) 
    try:
        result = result.strip()
        if result.startswith('```json'):
            result = result.split('```json')[1].split('```')[0].strip()
        elif result.startswith('```'):
            result = result.split('```')[1].split('```')[0].strip()
                
        final_result = json.loads(result)
        result_construct = final_result["construct"]
    except Exception as parse_error:
        print(f"Error parsing intend response: {str(parse_error)}")                 
        result_construct =  "an error occured"

    return result_construct