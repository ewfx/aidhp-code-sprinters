import os
import httpx
import logging
import time
import openai
from openai import OpenAI
from typing import Dict, Any, List, Optional
import json
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai



def call_openai_service(system_prompt: str, user_prompt: str,logger) -> str:
    start_time = time.time()
    logger.info("Starting OpenAI translation request")
    logger.info(f"System prompt length: {len(system_prompt)}, User prompt length: {len(user_prompt)}")
    
    try:
        logger.info("Sending request to OpenAI API (model: gpt-4o)")
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
        logger.info(f"OpenAI response received in {time.time() - start_time:.2f} seconds")
        logger.info(f"Response length: {len(result)} characters")
        
        return result
    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}", exc_info=True)
        raise Exception(f"OpenAI translation failed: {str(e)}")