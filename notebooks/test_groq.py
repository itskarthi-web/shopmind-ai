import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful shopping assistant."
        },
        {
            "role": "user",
            "content": "I want a gaming laptop under 60000 rupees. Suggest one in 2 lines."
        }
    ],
    max_tokens=200
)

print("✅ Groq API is working!")
print("\nAI says:")
print(response.choices[0].message.content)