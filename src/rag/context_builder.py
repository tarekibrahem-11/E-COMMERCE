def build_product_context(products):
    if not products:
        return "No relevant products were found."

    context_parts = []

    for product in products:
        context_parts.append(
            f"""
Product:
Name: {product["name"]}
Brand: {product["brand"]}
Category: {product["category"]}
Description: {product["description"]}
Price: {product["price"]} EGP
Rating: {product["rating"]}
Stock: {product["stock"]}
""".strip()
        )

    return "\n\n".join(context_parts)