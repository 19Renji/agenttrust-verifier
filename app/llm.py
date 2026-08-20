from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def execute_task(task):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are Agent B. Execute tasks concisely."},
            {"role": "user", "content": task},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content