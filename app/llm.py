from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def execute_task(task):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are Agent B. Execute the verified instruction concisely."
            },
            {
                "role": "user",
                "content": task
            }
        ],
        temperature=0.3,
        max_completion_tokens=200
    )

    return response.choices[0].message.content