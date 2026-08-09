import streamlit as st
import requests


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ShopMind AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

if "ai_response" not in st.session_state:
    st.session_state.ai_response = None

if "order_message" not in st.session_state:
    st.session_state.order_message = None


# ============================================================
# CUSTOM STREAMLIT THEME
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #050505;
        color: white;
    }

    /* Remove excessive top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Hide Streamlit menu */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #6c4cff;
        background-color: #111111;
        color: white;
        font-weight: 600;
        transition: 0.2s;
    }

    .stButton > button:hover {
        border-color: #9d7cff;
        color: #ffffff;
        background-color: #21134f;
    }

    /* Inputs */
    .stTextInput input {
        background-color: #15151c;
        color: white;
        border: 1px solid #353545;
        border-radius: 10px;
    }

    /* Selectbox */
    .stSelectbox div {
        border-radius: 10px;
    }

    /* Product cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #111116;
        border: 1px solid #292936;
        border-radius: 16px;
        padding: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_products():
    """Get products from FastAPI backend."""

    try:
        response = requests.get(
            f"{BACKEND_URL}/products",
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        # Handle both:
        # [{"id": 1, ...}]
        # {"products": [...]}

        if isinstance(data, dict):
            return data.get("products", [])

        return data

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to backend: {e}")
        return []


def get_product(product_id):
    """Get a single product."""

    try:
        response = requests.get(
            f"{BACKEND_URL}/products/{product_id}",
            timeout=5
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Could not load product: {e}")
        return None


def ask_ai(question):
    """Send question to ShopMind AI."""

    try:
        response = requests.post(
            f"{BACKEND_URL}/ai",
            json={
                "question": question
            },
            timeout=60
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e)
        }


def create_order(customer_name, product_id, quantity):
    """Create order through FastAPI."""

    try:
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json={
                "customer_name": customer_name,
                "product_id": product_id,
                "quantity": quantity
            },
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e)
        }


# ============================================================
# NAVIGATION
# ============================================================

if st.session_state.selected_product is None:

    # ========================================================
    # HERO SECTION
    # ========================================================

    st.write("")

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:

        st.markdown(
            "### 🟣 S H O P M I N D   A S S I S T A N T"
        )

        st.title("Ask anything about our products.")

        st.write(
            "Discover products, compare options and make "
            "smarter buying decisions with ShopMind AI."
        )

    st.divider()


    # ========================================================
    # AI ASSISTANT
    # ========================================================

    st.subheader("🤖 ShopMind AI")

    question = st.text_input(
        "Ask ShopMind AI",
        placeholder="What is the price of NovaBook Pro?",
        key="ai_question"
    )

    ask_button = st.button(
        "✨ ASK SHOPMIND AI",
        use_container_width=False
    )

    if ask_button:

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("ShopMind AI is thinking..."):

                result = ask_ai(question)

            st.session_state.ai_response = result


    # AI RESPONSE

    if st.session_state.ai_response:

        st.divider()

        st.subheader("💡 AI Response")

        result = st.session_state.ai_response

        if "error" in result:

            st.error(result["error"])

        else:

            # Try common response fields
            answer = (
                result.get("answer")
                or result.get("response")
                or result.get("message")
                or result
            )

            st.info(answer)


    st.divider()


    # ========================================================
    # PRODUCT DISCOVERY
    # ========================================================

    st.markdown("### 🟣 P R O D U C T   D I S C O V E R Y")

    st.header("Explore Products")

    products = get_products()


    # ========================================================
    # SEARCH
    # ========================================================

    search = st.text_input(
        "Search products",
        placeholder="Search for laptops, phones, headphones..."
    )


    # Filter products

    if search.strip():

        search_lower = search.lower()

        products = [
            product
            for product in products
            if search_lower in str(
                product.get("name", "")
            ).lower()
            or search_lower in str(
                product.get("description", "")
            ).lower()
        ]


    # ========================================================
    # PRODUCT GRID
    # ========================================================

    if not products:

        st.warning("No products found.")

    else:

        # Three-column product grid

        for start in range(0, len(products), 3):

            row = products[start:start + 3]

            columns = st.columns(3)

            for column, product in zip(columns, row):

                with column:

                    with st.container(border=True):

                        product_id = product.get(
                            "id",
                            product.get("product_id")
                        )

                        product_name = product.get(
                            "name",
                            product.get(
                                "product_name",
                                "Unnamed Product"
                            )
                        )

                        price = product.get(
                            "price",
                            product.get(
                                "product_price",
                                "N/A"
                            )
                        )

                        description = product.get(
                            "description",
                            "No description available."
                        )

                        category = product.get(
                            "category",
                            "Product"
                        )

                        st.markdown(
                            f"### 🛍️ {product_name}"
                        )

                        st.caption(
                            f"📂 {category}"
                        )

                        st.write(
                            str(description)[:120]
                            + (
                                "..."
                                if len(str(description)) > 120
                                else ""
                            )
                        )

                        st.markdown(
                            f"### ₹{price}"
                        )

                        if st.button(
                            "VIEW PRODUCT →",
                            key=f"view_{product_id}",
                            use_container_width=True
                        ):

                            # IMPORTANT:
                            # Save product in session state
                            st.session_state.selected_product = (
                                product_id
                            )

                            # Reload page
                            st.rerun()


# ============================================================
# PRODUCT DETAIL PAGE
# ============================================================

else:

    # ========================================================
    # BACK BUTTON
    # ========================================================

    if st.button("← BACK TO PRODUCTS"):

        st.session_state.selected_product = None

        st.rerun()


    st.divider()


    # ========================================================
    # LOAD PRODUCT
    # ========================================================

    product_id = st.session_state.selected_product

    product = get_product(product_id)


    if not product:

        st.error("Product could not be loaded.")

        if st.button("Return to products"):

            st.session_state.selected_product = None

            st.rerun()

    else:

        # Handle API response if wrapped
        if isinstance(product, dict):

            if "product" in product:
                product = product["product"]


        product_name = product.get(
            "name",
            product.get(
                "product_name",
                "Product"
            )
        )

        price = product.get(
            "price",
            product.get(
                "product_price",
                "N/A"
            )
        )

        description = product.get(
            "description",
            "No description available."
        )

        category = product.get(
            "category",
            "Product"
        )

        stock = product.get(
            "stock",
            product.get(
                "quantity",
                "Available"
            )
        )


        # ====================================================
        # PRODUCT HEADER
        # ====================================================

        st.markdown(
            "### 🟣 PRODUCT DETAILS"
        )

        st.title(product_name)

        st.write(
            f"📂 **Category:** {category}"
        )

        st.markdown(
            f"## ₹{price}"
        )

        st.divider()


        # ====================================================
        # PRODUCT INFORMATION
        # ====================================================

        left, right = st.columns([2, 1])


        with left:

            st.subheader("About this product")

            st.write(description)

            st.write("")

            st.success(
                f"📦 Stock / Availability: {stock}"
            )


        with right:

            st.subheader("🛒 Buy Product")

            customer_name = st.text_input(
                "Customer Name",
                placeholder="Enter your name"
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=10,
                value=1,
                step=1
            )


            if st.button(
                "🛒 PLACE ORDER",
                use_container_width=True
            ):

                if not customer_name.strip():

                    st.warning(
                        "Please enter your name."
                    )

                else:

                    with st.spinner(
                        "Creating your order..."
                    ):

                        result = create_order(
                            customer_name,
                            product_id,
                            quantity
                        )


                    if "error" in result:

                        st.error(
                            result["error"]
                        )

                    else:

                        st.success(
                            "🎉 Order created successfully!"
                        )

                        st.json(result)


        st.divider()


        # ====================================================
        # ASK AI ABOUT THIS PRODUCT
        # ====================================================

        st.subheader(
            "🤖 Ask ShopMind AI about this product"
        )

        product_question = st.text_input(
            "Product question",
            placeholder=(
                f"Is {product_name} worth buying?"
            ),
            key=f"product_question_{product_id}"
        )


        if st.button(
            "ASK AI ABOUT THIS PRODUCT",
            key=f"ask_product_{product_id}"
        ):

            if not product_question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                full_question = (
                    f"Regarding the product "
                    f"'{product_name}': "
                    f"{product_question}"
                )

                with st.spinner(
                    "ShopMind AI is analyzing..."
                ):

                    result = ask_ai(full_question)


                if "error" in result:

                    st.error(result["error"])

                else:

                    answer = (
                        result.get("answer")
                        or result.get("response")
                        or result.get("message")
                        or result
                    )

                    st.info(answer)