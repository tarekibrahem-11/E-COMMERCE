const productsContainer = document.getElementById("productsContainer");
const searchInput = document.getElementById("searchInput");
const categoryFilter = document.getElementById("categoryFilter");
const cartCount = document.getElementById("cartCount");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");

let currentProducts = [];


/* =========================================================
   PRODUCTS
========================================================= */

// Load all products
async function loadProducts() {
    try {
        const response = await fetch("/products");

        if (!response.ok) {
            throw new Error("Failed to load products");
        }

        const products = await response.json();

        currentProducts = products;

        renderProducts(products);
        updateCartCount();

    } catch (error) {
        console.error(error);

        productsContainer.innerHTML = `
            <p class="error-message">
                Failed to load products.
            </p>
        `;
    }
}


// Search products
async function searchProducts() {
    const query = searchInput.value.trim();
    const category = categoryFilter.value;

    try {
        let products;

        if (query) {
            const response = await fetch(
                `/api/products/search?q=${encodeURIComponent(query)}`
            );

            if (!response.ok) {
                throw new Error("Search failed");
            }

            products = await response.json();

        } else {
            const response = await fetch("/products");

            if (!response.ok) {
                throw new Error("Failed to load products");
            }

            products = await response.json();
        }


        // Category filter
        if (category) {
            products = products.filter(
                product => product.category === category
            );
        }

        currentProducts = products;

        renderProducts(products);

    } catch (error) {
        console.error(error);

        productsContainer.innerHTML = `
            <p class="error-message">
                Search failed.
            </p>
        `;
    }
}


// Render products
function renderProducts(products) {
    productsContainer.innerHTML = "";

    if (!products || products.length === 0) {
        productsContainer.innerHTML = `
            <p class="empty-state">
                No products found.
            </p>
        `;

        return;
    }


    products.forEach(product => {
        const card = document.createElement("div");

        card.className = "product-card";

        card.innerHTML = `
            <div class="product-image">
                <span>${product.category}</span>
            </div>

            <div class="product-info">

                <p class="product-brand">
                    ${product.brand}
                </p>

                <h3>
                    ${product.name}
                </h3>

                <p class="product-description">
                    ${product.description}
                </p>

                <div class="product-bottom">

                    <strong>
                        ${Number(product.price).toLocaleString()} EGP
                    </strong>

                    <span>
                        ★ ${product.rating}
                    </span>

                </div>

                <button class="add-cart-btn">
                    Add to cart
                </button>

            </div>
        `;


        const addButton = card.querySelector(".add-cart-btn");

        addButton.addEventListener("click", () => {
            addToCart(product);
        });


        productsContainer.appendChild(card);
    });
}


/* =========================================================
   CART
========================================================= */

// Add product to real backend cart
async function addToCart(product) {
    try {
        const response = await fetch(
            `/api/products/cart/add?product_id=${product.id}&quantity=1`,
            {
                method: "POST"
            }
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error("Failed to add product");
        }


        if (data.error) {
            addMessage(data.error, "ai");
            return;
        }


        addMessage(
            `${product.name} has been added to your cart.`,
            "ai"
        );


        updateCartCount();

    } catch (error) {
        console.error(error);

        addMessage(
            "Something went wrong while adding the product to your cart.",
            "ai"
        );
    }
}


// Get cart from backend
async function getCart() {
    const response = await fetch("/api/products/cart");

    if (!response.ok) {
        throw new Error("Failed to load cart");
    }

    return await response.json();
}


// Update cart count
async function updateCartCount() {
    try {
        const cart = await getCart();

        const totalItems = cart.items.reduce(
            (total, item) => total + item.quantity,
            0
        );

        cartCount.textContent = totalItems;

    } catch (error) {
        console.error(error);

        cartCount.textContent = "0";
    }
}


// Show cart
async function showCart() {
    try {
        const cart = await getCart();

        if (!cart.items || cart.items.length === 0) {
            addMessage(
                "Your cart is empty.",
                "ai"
            );

            return;
        }


        let message = `
            <strong>Your Cart</strong><br><br>
        `;


        cart.items.forEach(item => {
            message += `
                ${item.name} × ${item.quantity}
                — ${Number(item.total).toLocaleString()} EGP
                <br>
            `;
        });


        message += `
            <br>
            <strong>
                Total: ${Number(cart.total_price).toLocaleString()} EGP
            </strong>
        `;


        addMessage(message, "ai");

    } catch (error) {
        console.error(error);

        addMessage(
            "Failed to load your cart.",
            "ai"
        );
    }
}


/* =========================================================
   CHECKOUT
========================================================= */

async function checkout() {
    try {
        const response = await fetch(
            "/api/products/checkout",
            {
                method: "POST"
            }
        );


        const data = await response.json();


        if (data.error) {
            addMessage(
                data.error,
                "ai"
            );

            return;
        }


        addMessage(
            `
            <strong>Order placed successfully!</strong><br><br>
            Order ID: ${data.order_id}<br>
            Total: ${Number(data.total_price).toLocaleString()} EGP<br>
            Status: ${data.status}
            `,
            "ai"
        );


        updateCartCount();

    } catch (error) {
        console.error(error);

        addMessage(
            "Checkout failed.",
            "ai"
        );
    }
}


/* =========================================================
   ORDERS
========================================================= */

async function showOrders() {
    try {
        const response = await fetch(
            "/api/products/orders"
        );


        if (!response.ok) {
            throw new Error("Failed to load orders");
        }


        const orders = await response.json();


        if (!orders || orders.length === 0) {
            addMessage(
                "You don't have any orders yet.",
                "ai"
            );

            return;
        }


        let message = `
            <strong>Your Orders</strong><br><br>
        `;


        orders.forEach(order => {
            message += `
                Order #${order.order_id}
                — ${Number(order.total_price).toLocaleString()} EGP
                — ${order.status}
                <br>
            `;
        });


        addMessage(message, "ai");

    } catch (error) {
        console.error(error);

        addMessage(
            "Failed to load your orders.",
            "ai"
        );
    }
}


/* =========================================================
   AI CHAT
========================================================= */

function addMessage(text, sender = "ai") {
    const message = document.createElement("div");

    message.className = `message ${sender}-message`;

    const icon = sender === "ai"
        ? "🤖"
        : "👤";


    message.innerHTML = `
        <div class="message-icon">
            ${icon}
        </div>

        <div class="message-content">
            <p>${text}</p>
        </div>
    `;


    chatMessages.appendChild(message);

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


async function sendMessage() {
    const message = chatInput.value.trim();

    if (!message) {
        return;
    }


    // Show user message
    addMessage(
        message,
        "user"
    );


    chatInput.value = "";


    try {
        const response = await fetch(
            `/api/products/agent?query=${encodeURIComponent(message)}`,
            {
                method: "POST"
            }
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail || "AI Agent request failed"
            );
        }


        if (data.answer) {
            addMessage(
                data.answer,
                "ai"
            );
        }

        else if (data.error) {
            addMessage(
                `Sorry, something went wrong: ${data.error}`,
                "ai"
            );
        }

        else {
            addMessage(
                "Sorry, I couldn't generate an answer.",
                "ai"
            );
        }


        // Refresh cart count
        updateCartCount();

    } catch (error) {
        console.error(error);

        addMessage(
            "Something went wrong while talking to the AI assistant.",
            "ai"
        );
    }
}


// Enter key
function handleChat(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}


/* =========================================================
   SEMANTIC SEARCH
========================================================= */

async function semanticSearch() {
    const query = chatInput.value.trim();


    if (!query) {
        addMessage(
            "Type what you're looking for first.",
            "ai"
        );

        return;
    }


    try {
        const response = await fetch(
            `/api/products/semantic-search?q=${encodeURIComponent(query)}`
        );


        if (!response.ok) {
            throw new Error(
                "Semantic search failed"
            );
        }


        const products = await response.json();


        currentProducts = products;

        renderProducts(products);


        addMessage(
            `Semantic Search found ${products.length} relevant products.`,
            "ai"
        );

    } catch (error) {
        console.error(error);

        addMessage(
            "Semantic Search failed.",
            "ai"
        );
    }
}


/* =========================================================
   RAG
========================================================= */

async function askRAG() {
    const query = chatInput.value.trim();


    if (!query) {
        addMessage(
            "Type a product question first.",
            "ai"
        );

        return;
    }


    try {
        const response = await fetch(
            `/api/products/rag-answer?q=${encodeURIComponent(query)}`
        );


        if (!response.ok) {
            throw new Error(
                "RAG request failed"
            );
        }


        const data = await response.json();


        if (data.answer) {
            addMessage(
                data.answer,
                "ai"
            );
        }

        else {
            addMessage(
                "I couldn't find an answer.",
                "ai"
            );
        }

    } catch (error) {
        console.error(error);

        addMessage(
            "RAG request failed.",
            "ai"
        );
    }
}


/* =========================================================
   COMPARE
========================================================= */

async function compareProducts() {
    if (!currentProducts || currentProducts.length < 2) {
        addMessage(
            "Please search for at least two products first.",
            "ai"
        );

        return;
    }


    const product1 = currentProducts[0];
    const product2 = currentProducts[1];


    try {
        const response = await fetch(
            `/api/products/compare?product_id_1=${product1.id}&product_id_2=${product2.id}`
        );


        if (!response.ok) {
            throw new Error(
                "Comparison failed"
            );
        }


        const data = await response.json();


        const first = data.product_1;
        const second = data.product_2;


        const message = `
            <strong>Product Comparison</strong><br><br>

            <strong>${first.name}</strong><br>
            Price: ${Number(first.price).toLocaleString()} EGP<br>
            Rating: ${first.rating}<br>
            Stock: ${first.stock}
            <br><br>

            <strong>${second.name}</strong><br>
            Price: ${Number(second.price).toLocaleString()} EGP<br>
            Rating: ${second.rating}<br>
            Stock: ${second.stock}
        `;


        addMessage(
            message,
            "ai"
        );

    } catch (error) {
        console.error(error);

        addMessage(
            "Failed to compare products.",
            "ai"
        );
    }
}


/* =========================================================
   CART BUTTON
========================================================= */

const cartButton = document.querySelector(
    ".cart-button"
);


if (cartButton) {
    cartButton.addEventListener(
        "click",
        showCart
    );
}


/* =========================================================
   SEARCH / FILTER EVENTS
========================================================= */

searchInput.addEventListener(
    "input",
    searchProducts
);


categoryFilter.addEventListener(
    "change",
    searchProducts
);


/* =========================================================
   INITIAL LOAD
========================================================= */

loadProducts();