from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def execute_task(task):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"user",
                "content":task
            }
        ]
    )

    return response.choices[0].message.content