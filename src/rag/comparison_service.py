import os

from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from src.ml.product_comparison import compare_products

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def compare_products_with_ai(
    product_id_1: int,
    product_id_2: int,
    query: str,
    db: Session
):
    comparison = compare_products(
        product_id_1=product_id_1,
        product_id_2=product_id_2,
        db=db
    )

    if not comparison:
        return {
            "error": "One or both products were not found."
        }

    product_1 = comparison["product_1"]
    product_2 = comparison["product_2"]

    context = f"""
Product 1:
Name: {product_1.name}
Brand: {product_1.brand}
Category: {product_1.category}
Description: {product_1.description}
Price: {product_1.price} EGP
Rating: {product_1.rating}
Stock: {product_1.stock}

Product 2:
Name: {product_2.name}
Brand: {product_2.brand}
Category: {product_2.category}
Description: {product_2.description}
Price: {product_2.price} EGP
Rating: {product_2.rating}
Stock: {product_2.stock}
"""

    prompt = f"""
You are an AI shopping assistant.

Compare the two products using ONLY the provided information.

Do not invent specifications or features.

Explain:
1. Main differences
2. Price difference
3. Rating difference
4. Stock difference
5. Which product is better for the user's request
6. Final recommendation

User request:
{query}

Product information:
{context}
"""

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    return {
        "query": query,
        "comparison": {
            "product_1": product_1.name,
            "product_2": product_2.name
        },
        "answer": response.text
    }