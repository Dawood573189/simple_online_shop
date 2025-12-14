import streamlit as st
import random

# ---------------- Backend Data ----------------

# Static product list (Product ID -> dict)
PRODUCTS = {
    1: {"name": "Laptop", "price": 120000},
    2: {"name": "Smartphone", "price": 60000},
    3: {"name": "Headphones", "price": 5000},
    4: {"name": "Keyboard", "price": 2500},
    5: {"name": "Mouse", "price": 1500},
}

# Use session_state to persist cart between button clicks
# cart will be a list of dicts: {"product_id": int, "quantity": int}
if "cart" not in st.session_state:
    st.session_state["cart"] = []

cart = st.session_state["cart"]


# ---------------- Functions (Logic) ----------------

def show_products():
    """Return all available products as list of (id, name, price)."""
    data = []
    for pid, info in PRODUCTS.items():
        data.append((pid, info["name"], info["price"]))
    return data


def find_cart_item(cart_list, product_id):
    """Helper: find cart item dict by product_id."""
    for item in cart_list:
        if item["product_id"] == product_id:
            return item
    return None


def add_to_cart(cart_list, product_id, quantity):
    """Add a product with quantity to cart_list if it exists.
       If already in cart, increase its quantity.
    """
    if product_id not in PRODUCTS:
        return False, "Invalid Product ID"

    if quantity <= 0:
        return False, "Quantity must be at least 1"

    existing_item = find_cart_item(cart_list, product_id)
    if existing_item:
        existing_item["quantity"] += quantity
    else:
        cart_list.append({"product_id": product_id, "quantity": quantity})

    return True, None


def view_cart(cart_list):
    """Return details of items in the cart."""
    items = []
    for item in cart_list:
        pid = item["product_id"]
        qty = item["quantity"]
        prod = PRODUCTS.get(pid)
        if prod:
            items.append(
                {
                    "product_id": pid,
                    "name": prod["name"],
                    "price": prod["price"],
                    "quantity": qty,
                    "subtotal": prod["price"] * qty,
                }
            )
    return items


def remove_from_cart(cart_list, product_id, quantity):
    """Remove given quantity of product_id from cart_list.
       If quantity >= existing quantity, remove the item completely.
    """
    existing_item = find_cart_item(cart_list, product_id)
    if not existing_item:
        return False, "Item not found in cart"

    if quantity <= 0:
        return False, "Quantity must be at least 1"

    if quantity >= existing_item["quantity"]:
        cart_list.remove(existing_item)
    else:
        existing_item["quantity"] -= quantity

    return True, None


def calculate_total(cart_list):
    """Calculate total price of all items in cart_list."""
    total = 0
    for item in cart_list:
        pid = item["product_id"]
        qty = item["quantity"]
        prod = PRODUCTS.get(pid)
        if prod:
            total += prod["price"] * qty
    return total


def checkout(cart_list):
    """Return total bill and then clear the cart_list."""
    total = calculate_total(cart_list)
    cart_list.clear()
    return total


# ---------------- Streamlit UI ----------------

st.title("🛒 Simple Online Shop ")
st.write("Menu-driven Online Shop built with Python functions and Streamlit, including quantity in cart.")

menu = st.sidebar.selectbox(
    "Select Action",
    ["View Products", "Add to Cart", "View Cart", "Remove Item", "Checkout", "Debug: Show Raw Cart"],
)

# --- View Products ---
if menu == "View Products":
    st.header("📦 Available Products")
    products_data = show_products()

    st.write("Here are all the products:")
    for pid, name, price in products_data:
        st.write(f"**ID:** {pid} | **Name:** {name} | **Price:** Rs {price}")

# --- Add to Cart ---
elif menu == "Add to Cart":
    st.header("➕ Add Product to Cart")

    products_data = show_products()
    st.subheader("Product List")
    for pid, name, price in products_data:
        st.write(f"**ID:** {pid} | **Name:** {name} | **Price:** Rs {price}")

    prod_id = st.number_input("Enter Product ID to add", min_value=1, step=1)
    qty = st.number_input("Enter Quantity", min_value=1, step=1, value=1)

    if st.button("Add to Cart"):
        success, err = add_to_cart(cart, prod_id, qty)
        if success:
            st.success(f"{qty} unit(s) of Product ID {prod_id} added to cart!")
        else:
            st.error(err)

# --- View Cart ---
elif menu == "View Cart":
    st.header("🛍️ Your Cart")

    items = view_cart(cart)

    if not items:
        st.info("Your cart is empty.")
    else:
        for item in items:
            st.write(
                f"**ID:** {item['product_id']} | "
                f"**Name:** {item['name']} | "
                f"**Price:** Rs {item['price']} | "
                f"**Qty:** {item['quantity']} | "
                f"**Subtotal:** Rs {item['subtotal']}"
            )

        total = calculate_total(cart)
        st.subheader(f"Total: Rs {total}")

# --- Remove Item ---
elif menu == "Remove Item":
    st.header("➖ Remove Item from Cart")

    if not cart:
        st.info("Your cart is empty. Nothing to remove.")
    else:
        items = view_cart(cart)
        st.subheader("Items in Cart")
        for item in items:
            st.write(
                f"**ID:** {item['product_id']} | "
                f"**Name:** {item['name']} | "
                f"**Price:** Rs {item['price']} | "
                f"**Qty:** {item['quantity']} | "
                f"**Subtotal:** Rs {item['subtotal']}"
            )

        prod_id = st.number_input("Enter Product ID to remove", min_value=1, step=1)
        qty = st.number_input("Enter Quantity to remove", min_value=1, step=1, value=1)

        if st.button("Remove from Cart"):
            success, err = remove_from_cart(cart, prod_id, qty)
            if success:
                st.success(f"{qty} unit(s) of Product ID {prod_id} removed from cart.")
            else:
                st.error(err)

# --- Checkout ---
elif menu == "Checkout":
    st.header("💳 Checkout")

    if not cart:
        st.info("Your cart is empty. Please add items before checkout.")
    else:
        items = view_cart(cart)
        st.subheader("Cart Summary")
        for item in items:
            st.write(
                f"**ID:** {item['product_id']} | "
                f"**Name:** {item['name']} | "
                f"Price:** Rs {item['price']} | "
                f"Qty:** {item['quantity']} | "
                f"Subtotal:** Rs {item['subtotal']}"
            )

        if st.button("Confirm Checkout"):
            total = checkout(cart)
            st.success(f"Checkout successful! Your final bill is Rs {total}.")
            st.info("Cart is now empty.")

# --- Debug: Show Raw Cart ---
elif menu == "Debug: Show Raw Cart":
    st.header("🧪 Debug View - Raw Cart List")
    st.write(cart)
