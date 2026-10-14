import os

from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from src.rag.context_builder import build_product_context
from src.rag.product_knowledge import get_product_knowledge

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def answer_product_question(query: str, db: Session):
    # 1. Retrieve relevant products
    products = get_product_knowledge(query=query, db=db, limit=5)

    # 2. No products found
    if not products:
        return {
            "query": query,
            "answer": "I couldn't find relevant products.",
            "products": [],
        }

    # 3. Build context
    context = build_product_context(products)

    # 4. Build prompt
    prompt = f"""
You are an AI shopping assistant.

Answer the user's question using ONLY the product
information provided in the context.

Do not invent product information.

If the information is not available in the context,
say that you don't have enough information.

Product Context:
{context}

User Question:
{query}
"""

    # 5. Generate answer using Gemini
    response = client.models.generate_content(model="gemini-3.7-flash", contents=prompt)

    answer = response.text

    # 6. Return result
    return {"query": query, "answer": answer, "products": products}
