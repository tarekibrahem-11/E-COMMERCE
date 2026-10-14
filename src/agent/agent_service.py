import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from sqlalchemy.orm import Session

from src.agent.tools import (
    add_to_cart_tool,
    cart_tool,
    checkout_tool,
    compare_tool,
    filter_products_by_price,
    get_best_products,
    orders_tool,
    rag_tool,
    recommend_tool,
    search_tool,
    semantic_search_tool,
)

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ============================================================
# HELPERS
# ============================================================


def product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "brand": product.brand,
        "description": product.description,
        "price": product.price,
        "rating": product.rating,
        "stock": product.stock,
    }


def clean_json_response(response_text: str) -> str:
    """
    Remove markdown code fences if Gemini returns JSON
    wrapped inside ```json ... ```.
    """
    response_text = response_text.strip()

    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "")
        response_text = response_text.strip()

    return response_text


def handle_direct_intent(query: str, db: Session):
    """
    Handle simple deterministic requests without using Gemini.
    """

    query_lower = query.lower().strip()

    # ========================================================
    # SHOW CART
    # ========================================================

    if query_lower in [
        "show my cart",
        "view my cart",
        "open my cart",
        "cart",
    ]:
        cart = cart_tool(db)

        if not cart["items"]:
            answer = "Your shopping cart is currently empty."
        else:
            answer = (
                f"Your cart contains {len(cart['items'])} item(s) "
                f"with a total price of {cart['total_price']} EGP."
            )

        return {
            "query": query,
            "answer": answer,
            "steps": [
                {
                    "action": "cart",
                    "cart": cart,
                }
            ],
        }

    # ========================================================
    # SHOW ORDERS
    # ========================================================

    if query_lower in [
        "show my orders",
        "view my orders",
        "order history",
        "my orders",
    ]:
        orders = orders_tool(db)

        if not orders:
            answer = "You don't have any previous orders."
        else:
            answer = f"You have {len(orders)} previous order(s)."

        return {
            "query": query,
            "answer": answer,
            "steps": [
                {
                    "action": "orders",
                    "orders": orders,
                }
            ],
        }

    return None


# ============================================================
# MAIN AGENT
# ============================================================


def run_agent(query: str, db: Session):
    # ========================================================
    # PLANNER PROMPT
    # ========================================================

    prompt = f"""
You are an AI shopping agent for an e-commerce system.

Your job is to understand the user's request and create
a sequence of actions to solve it.

Available actions:

1. search

Use for exact keyword/product searches.

2. recommendation

Use when the user asks for recommendations.

3. semantic_search

Use when the user describes what they want in natural language.

4. filter_by_price

Use when the user specifies a maximum price.

5. get_best_products

Use when the user asks for the best products or best two/three products.

6. comparison

Use when the user wants to compare products.

7. rag

Use when the user asks a question about products.

8. add_to_cart

Use when the user wants to add a product to the cart.

Important rules for add_to_cart:

- First find the requested product using search or semantic_search.
- Do NOT invent product IDs.
- The product_id must come from the search results.
- Use quantity=1 if the user does not specify a quantity.

9. orders

Use when the user asks about previous orders.

10. cart

Use when the user asks to see or check their shopping cart.

For cart:

- Do not provide any arguments.
- The system will automatically retrieve the current cart.

11. checkout

Use when the user wants to complete the purchase or checkout.

For checkout:

- Do not provide any arguments.
- The system will automatically use the current shopping cart.

Return ONLY raw JSON.

Do NOT use markdown.

Do NOT wrap the JSON in ```json or ```.

Format:

{{
    "steps": [
        {{
            "action": "action_name",
            "arguments": {{}}
        }}
    ]
}}

Example 1:

User:

I need a laptop for AI under 60000 EGP.

Recommend the best two and compare them.

Return:

{{
    "steps": [
        {{
            "action": "semantic_search",
            "arguments": {{
                "query": "laptop for AI and programming"
            }}
        }},
        {{
            "action": "filter_by_price",
            "arguments": {{
                "max_price": 60000
            }}
        }},
        {{
            "action": "get_best_products",
            "arguments": {{
                "limit": 2
            }}
        }},
        {{
            "action": "comparison",
            "arguments": {{}}
        }}
    ]
}}

Example 2:

User:

Add Lenovo Legion 5 to my cart.

Return:

{{
    "steps": [
        {{
            "action": "search",
            "arguments": {{
                "query": "Lenovo Legion 5"
            }}
        }},
        {{
            "action": "add_to_cart",
            "arguments": {{
                "quantity": 1
            }}
        }}
    ]
}}

Important:

For comparison, DO NOT provide product IDs.

The system will automatically compare the products selected
by the previous get_best_products step.

For add_to_cart:

DO NOT provide product_id in the planner arguments.

The system will automatically use the product selected
by the previous search or semantic_search step.

User request:

{query}
"""

    # ========================================================
    # SIMPLE INTENT DETECTION
    # ========================================================

    direct_result = handle_direct_intent(query, db)

    if direct_result is not None:
        return direct_result

    # ========================================================
    # GENERATE PLAN
    # ========================================================

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.7-flash",
                contents=prompt,
            )
            break

        except errors.APIError as e:
            print("PLANNER GEMINI ERROR:", e)

            error_message = str(e)

            # ------------------------------------------------
            # QUOTA EXCEEDED
            # ------------------------------------------------

            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                return {
                    "query": query,
                    "answer": (
                        "The AI service has reached its current usage "
                        "limit. Please try again later."
                    ),
                    "steps": [],
                    "planner_error": error_message,
                }

            # ------------------------------------------------
            # TEMPORARY SERVER/API ERROR
            # ------------------------------------------------

            if attempt < max_retries - 1:
                time.sleep(5)

            else:
                return {
                    "query": query,
                    "answer": (
                        "The AI service is temporarily unavailable. "
                        "Please try again later."
                    ),
                    "steps": [],
                    "planner_error": error_message,
                }

    # ========================================================
    # PARSE PLAN
    # ========================================================

    response_text = clean_json_response(response.text)

    try:
        plan = json.loads(response_text)

    except json.JSONDecodeError:
        return {
            "error": "Agent returned invalid JSON",
            "raw_response": response.text,
        }

    steps = plan.get("steps", [])

    if not steps:
        return {"error": "Agent returned an empty plan"}

    # ========================================================
    # EXECUTION STATE
    # ========================================================

    current_products = []
    execution_results = []

    # ========================================================
    # EXECUTE STEPS
    # ========================================================

    for step in steps:
        action = step.get("action")
        arguments = step.get("arguments", {})

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        if action == "search":
            products = search_tool(
                query=arguments.get("query", query),
                db=db,
            )

            current_products = products

            execution_results.append(
                {
                    "action": action,
                    "results": [product_to_dict(product) for product in products],
                }
            )

        # ----------------------------------------------------
        # RECOMMENDATION
        # ----------------------------------------------------

        elif action == "recommendation":
            products = recommend_tool(
                query=arguments.get("query", query),
                db=db,
            )

            current_products = products

            execution_results.append(
                {
                    "action": action,
                    "results": [product_to_dict(product) for product in products],
                }
            )

        # ----------------------------------------------------
        # SEMANTIC SEARCH
        # ----------------------------------------------------

        elif action == "semantic_search":
            products = semantic_search_tool(
                query=arguments.get("query", query),
                db=db,
            )

            current_products = products

            execution_results.append(
                {
                    "action": action,
                    "results": [product_to_dict(product) for product in products],
                }
            )

        # ----------------------------------------------------
        # FILTER BY PRICE
        # ----------------------------------------------------

        elif action == "filter_by_price":
            max_price = arguments.get("max_price")

            if max_price is None:
                return {"error": "max_price is required"}

            current_products = filter_products_by_price(
                products=current_products,
                max_price=max_price,
            )

            execution_results.append(
                {
                    "action": action,
                    "max_price": max_price,
                    "results": [
                        product_to_dict(product) for product in current_products
                    ],
                }
            )

        # ----------------------------------------------------
        # GET BEST PRODUCTS
        # ----------------------------------------------------

        elif action == "get_best_products":
            limit = arguments.get("limit", 2)

            current_products = get_best_products(
                products=current_products,
                limit=limit,
            )

            execution_results.append(
                {
                    "action": action,
                    "results": [
                        product_to_dict(product) for product in current_products
                    ],
                }
            )

        # ----------------------------------------------------
        # COMPARISON
        # ----------------------------------------------------

        elif action == "comparison":
            if len(current_products) < 2:
                return {"error": ("At least two products are required for comparison.")}

            product_1 = current_products[0]
            product_2 = current_products[1]

            result = compare_tool(
                product_id_1=product_1.id,
                product_id_2=product_2.id,
                db=db,
            )

            if not result:
                return {"error": "Products could not be compared."}

            execution_results.append(
                {
                    "action": action,
                    "result": {
                        "product_1": product_to_dict(result["product_1"]),
                        "product_2": product_to_dict(result["product_2"]),
                    },
                }
            )

        # ----------------------------------------------------
        # RAG
        # ----------------------------------------------------

        elif action == "rag":
            result = rag_tool(
                query=arguments.get("query", query),
                db=db,
            )

            execution_results.append(
                {
                    "action": action,
                    "result": result,
                }
            )

        # ----------------------------------------------------
        # ADD TO CART
        # ----------------------------------------------------

        elif action == "add_to_cart":
            quantity = arguments.get("quantity", 1)

            if not current_products:
                execution_results.append(
                    {
                        "action": action,
                        "result": {"error": "Product not found"},
                    }
                )

                continue

            # Get the product requested by the user

            requested_query = query.lower().strip()
            matched_product = None

            for product in current_products:
                product_name = product.name.lower().strip()

                # Exact product name match

                if product_name == requested_query:
                    matched_product = product
                    break

                # Product name exists inside user request

                if product_name in requested_query:
                    matched_product = product
                    break

            # No exact/strong match

            if matched_product is None:
                execution_results.append(
                    {
                        "action": action,
                        "result": {"error": ("The requested product was not found.")},
                    }
                )

                continue

            product = matched_product

            result = add_to_cart_tool(
                product_id=product.id,
                quantity=quantity,
                db=db,
            )

            if result is None:
                execution_results.append(
                    {
                        "action": action,
                        "result": {"error": "Product not found"},
                    }
                )

            elif isinstance(result, dict):
                execution_results.append(
                    {
                        "action": action,
                        "result": result,
                    }
                )

            else:
                execution_results.append(
                    {
                        "action": action,
                        "result": {
                            "message": "Product added to cart",
                            "product_id": result.product_id,
                            "quantity": result.quantity,
                        },
                    }
                )

        # ----------------------------------------------------
        # ORDERS
        # ----------------------------------------------------

        elif action == "orders":
            orders = orders_tool(db)

            execution_results.append(
                {
                    "action": action,
                    "orders": orders,
                }
            )

        # ----------------------------------------------------
        # CHECKOUT
        # ----------------------------------------------------

        elif action == "checkout":
            result = checkout_tool(db)

            execution_results.append(
                {
                    "action": action,
                    "result": result,
                }
            )

        # ----------------------------------------------------
        # CART
        # ----------------------------------------------------

        elif action == "cart":
            cart = cart_tool(db)

            execution_results.append(
                {
                    "action": action,
                    "cart": cart,
                }
            )

        # ----------------------------------------------------
        # UNKNOWN ACTION
        # ----------------------------------------------------

        else:
            return {"error": f"Unknown action: {action}"}

    # ========================================================
    # DIRECT RESPONSE FOR SIMPLE ACTIONS
    # ========================================================

    if len(execution_results) == 1:
        action = execution_results[0]["action"]

        # ----------------------------------------------------
        # CART RESPONSE
        # ----------------------------------------------------

        if action == "cart":
            cart = execution_results[0]["cart"]

            if not cart["items"]:
                answer = "Your shopping cart is currently empty."
            else:
                answer = (
                    f"Your cart contains "
                    f"{len(cart['items'])} item(s) "
                    f"with a total price of "
                    f"{cart['total_price']} EGP."
                )

            return {
                "query": query,
                "answer": answer,
                "steps": execution_results,
            }

        # ----------------------------------------------------
        # ORDERS RESPONSE
        # ----------------------------------------------------

        if action == "orders":
            orders = execution_results[0]["orders"]

            if not orders:
                answer = "You don't have any previous orders."
            else:
                answer = f"You have {len(orders)} previous order(s)."

            return {
                "query": query,
                "answer": answer,
                "steps": execution_results,
            }

        # ----------------------------------------------------
        # ADD TO CART RESPONSE
        # ----------------------------------------------------

        if action == "add_to_cart":
            result = execution_results[0]["result"]

            if "error" in result:
                return {
                    "query": query,
                    "answer": result["error"],
                    "steps": execution_results,
                }

            return {
                "query": query,
                "answer": ("The product was successfully added to your cart."),
                "steps": execution_results,
            }

        # ----------------------------------------------------
        # CHECKOUT RESPONSE
        # ----------------------------------------------------

        if action == "checkout":
            result = execution_results[0]["result"]

            if "error" in result:
                return {
                    "query": query,
                    "answer": result["error"],
                    "steps": execution_results,
                }

            return {
                "query": query,
                "answer": (
                    f"Your order was placed successfully.\n"
                    f"Order ID: {result['order_id']}\n"
                    f"Total: {result['total_price']} EGP\n"
                    f"Status: {result['status'].capitalize()}."
                ),
                "steps": execution_results,
            }

    # ========================================================
    # FINAL AI RESPONSE
    # ========================================================

    final_prompt = f"""
You are an AI shopping assistant.

Answer the user's request using ONLY the execution results below.

User request:

{query}

Execution results:

{
        json.dumps(
            execution_results,
            ensure_ascii=False,
            indent=2,
        )
    }

Instructions:

- Give a clear and helpful answer.
- Mention the recommended products.
- Mention their prices when relevant.
- If products were compared, explain the main difference.
- Respect the user's budget.
- All prices in this system are in EGP.
- NEVER use $, USD, or any other currency.
- Always write prices using EGP.
- Do not invent specifications or information.
- Do not mention internal tools, steps, actions, JSON, or the agent.
- Answer naturally as a shopping assistant.
"""

    # ========================================================
    # GENERATE FINAL ANSWER WITH RETRY
    # ========================================================

    max_retries = 3

    for attempt in range(max_retries):
        try:
            final_response = client.models.generate_content(
                model="gemini-3.7-flash",
                contents=final_prompt,
            )

            final_answer = final_response.text.strip()

            return {
                "query": query,
                "answer": final_answer,
                "steps": execution_results,
            }

        except errors.APIError as e:
            print("GEMINI ERROR:", e)

            error_message = str(e)

            # ------------------------------------------------
            # QUOTA EXCEEDED
            # ------------------------------------------------

            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                fallback_answer = "The AI service has reached its current usage limit."

                for execution in execution_results:
                    result = execution.get("result")

                    if isinstance(result, dict) and "error" in result:
                        fallback_answer = result["error"]
                        break

                    if execution["action"] == "add_to_cart" and isinstance(
                        result, dict
                    ):
                        quantity = result.get(
                            "quantity",
                            1,
                        )

                        fallback_answer = (
                            "The product was successfully "
                            "added to your cart. "
                            f"Quantity: {quantity}."
                        )
                        break

                    if execution["action"] == "checkout" and isinstance(
                        result,
                        dict,
                    ):
                        fallback_answer = (
                            "Your order was placed "
                            "successfully. "
                            f"Order ID: "
                            f"{result.get('order_id')}. "
                            f"Total: "
                            f"{result.get('total_price')} EGP. "
                            f"Status: "
                            f"{result.get('status', 'confirmed').capitalize()}."
                        )
                        break

                return {
                    "query": query,
                    "answer": fallback_answer,
                    "steps": execution_results,
                    "final_answer_error": error_message,
                }

            # ------------------------------------------------
            # TEMPORARY SERVER/API ERROR
            # ------------------------------------------------

            if attempt < max_retries - 1:
                time.sleep(2)

            else:
                fallback_answer = "I couldn't generate the final AI response right now."

                for execution in execution_results:
                    result = execution.get("result")

                    if isinstance(result, dict) and "error" in result:
                        fallback_answer = result["error"]
                        break

                    if execution["action"] == "add_to_cart" and isinstance(
                        result,
                        dict,
                    ):
                        quantity = result.get(
                            "quantity",
                            1,
                        )

                        fallback_answer = (
                            "The product was successfully "
                            "added to your cart. "
                            f"Quantity: {quantity}."
                        )
                        break

                    if execution["action"] == "checkout" and isinstance(
                        result,
                        dict,
                    ):
                        fallback_answer = (
                            "Your order was placed "
                            "successfully. "
                            f"Order ID: "
                            f"{result.get('order_id')}. "
                            f"Total: "
                            f"{result.get('total_price')} EGP. "
                            f"Status: "
                            f"{result.get('status', 'confirmed').capitalize()}."
                        )
                        break

                return {
                    "query": query,
                    "answer": fallback_answer,
                    "steps": execution_results,
                    "final_answer_error": error_message,
                }
