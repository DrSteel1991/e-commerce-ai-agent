def build_rag_prompt(question: str, context_chunks: list) -> str:
    context_text = "\n\n".join(
        [
            f"""
SOURCE {index + 1}
Filename: {chunk.filename}
Chunk ID: {chunk.id}
Content:
{chunk.content}
"""
            for index, chunk in enumerate(context_chunks)
        ]
    )

    return f"""
You are a helpful customer support assistant for an e-commerce platform.

Answer the user's question using the provided context.

Rules:
- If the context contains relevant policy information, answer clearly using that information.
- For vague questions like "Can I refund this?", explain the general refund/return policy from the context.
- Combine information from multiple sources when helpful.
- Only say "I don't have enough information to answer that." if the context is completely unrelated to the question.
- Keep the answer short and customer-friendly.
- Do not invent policies that are not in the context.

Context:
{context_text}

User question:
{question}

Final answer:
"""
