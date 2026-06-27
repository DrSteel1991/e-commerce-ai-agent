import os

from dotenv import load_dotenv
from openai import OpenAI

_ = load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_answer(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("OpenAI returned empty content")

    return content
