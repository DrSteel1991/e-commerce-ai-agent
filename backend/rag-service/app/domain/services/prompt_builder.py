def build_rag_prompt(question: str, chunks):
    context = "\n\n".join(chunk.content for chunk in chunks)

    return f"""
You are an AI customer support assistant.

Answer the user's question ONLY using the provided context.

If the answer cannot be found in the context,
say:

"I don't have enough information to answer that."

----------------------------
Context

{context}

----------------------------
Question

{question}

Answer:
"""
