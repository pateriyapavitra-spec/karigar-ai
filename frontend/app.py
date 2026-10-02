# ============================================================
# KARIGAR AI - STREAMLIT FRONTEND
# ============================================================

import streamlit as st
import requests


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "https://karigar-ai-e0n7.onrender.com"

st.set_page_config(
    page_title="KarigarAI",
    page_icon="🎨",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #faf7f2;
    }

    .main-title {
        font-size: 52px;
        font-weight: 800;
        text-align: center;
        color: #33251f;
        margin-top: 10px;
    }

    .highlight {
        color: #a0522d;
    }

    .subtitle {
        text-align: center;
        color: #786b63;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .intro {
        text-align: center;
        color: #6f655f;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .section-label {
        color: #a0522d;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .price-box {
        background-color: #f4e9df;
        padding: 22px;
        border-radius: 15px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .price-heading {
        font-size: 14px;
        color: #76675e;
    }

    .price-value {
        font-size: 38px;
        font-weight: 800;
        color: #984d2e;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "product" not in st.session_state:
    st.session_state.product = None

if "filename" not in st.session_state:
    st.session_state.filename = ""

if "price_result" not in st.session_state:
    st.session_state.price_result = None

if "product_id" not in st.session_state:
    st.session_state.product_id = None

if "dashboard_products" not in st.session_state:
    st.session_state.dashboard_products = None


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        Karigar<span class="highlight">AI</span>
    </div>

    <div class="subtitle">
        AI-Powered Product Studio for Artisans
    </div>

    <div class="intro">
        Turn your handmade craft into a marketplace-ready
        product using AI catalogue generation and smart pricing.
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# STEP 1 - UPLOAD PRODUCT
# ============================================================

st.markdown(
    '<div class="section-label">STEP 1</div>',
    unsafe_allow_html=True
)

st.header("📸 Upload Your Craft")

st.write(
    "Upload a clear image of your handcrafted product."
)

uploaded_file = st.file_uploader(
    "Choose Product Image",
    type=["jpg", "jpeg", "png", "webp"]
)


if uploaded_file is not None:

    image_col, info_col = st.columns([1, 1])

    with image_col:

        st.image(
            uploaded_file,
            caption="Product Image",
            use_container_width=True
        )

    with info_col:

        st.subheader("AI Product Analysis")

        st.write(
            "KarigarAI will analyze the image and generate "
            "marketplace catalogue information."
        )

        analyze_button = st.button(
            "✨ Analyze Product with AI",
            type="primary",
            use_container_width=True
        )

        if analyze_button:

            with st.spinner(
                "AI is analyzing your craft..."
            ):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/analyze-product",
                        files=files,
                        timeout=120
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state.product = (
                            data["product"]
                        )

                        st.session_state.filename = (
                            data.get(
                                "filename",
                                ""
                            )
                        )

                        # New image = new product workflow
                        st.session_state.product_id = None
                        st.session_state.price_result = None

                        st.success(
                            "Product analyzed successfully!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "AI analysis failed."
                        )

                        st.code(
                            response.text
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI. "
                        "Make sure the backend is running "
                        "on port 8000."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "AI analysis took too long. "
                        "Please try again."
                    )

                except Exception as error:

                    st.error(
                        f"Something went wrong: {error}"
                    )


# ============================================================
# STEP 2 - AI GENERATED CATALOGUE
# ============================================================

if st.session_state.product is not None:

    st.divider()

    st.markdown(
        '<div class="section-label">STEP 2</div>',
        unsafe_allow_html=True
    )

    st.header(
        "🤖 AI Generated Catalogue"
    )

    st.write(
        "Review the AI-generated information. "
        "You can edit anything before saving."
    )

    product = st.session_state.product

    # --------------------------------------------------------
    # PRODUCT NAME
    # --------------------------------------------------------

    product_name = st.text_input(
        "Product Name",
        value=product.get(
            "product_name",
            ""
        ),
        key="catalogue_product_name"
    )

    # --------------------------------------------------------
    # PRODUCT TYPE + MATERIAL
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        product_type = st.text_input(
            "Product Type",
            value=product.get(
                "product_type",
                ""
            ),
            key="catalogue_product_type"
        )

    with col2:

        material_data = product.get(
            "material",
            ""
        )

        if isinstance(
            material_data,
            list
        ):
            material_data = ", ".join(
                material_data
            )

        material = st.text_input(
            "Material",
            value=material_data,
            key="catalogue_material"
        )

    # --------------------------------------------------------
    # CRAFT STYLE + CATEGORY
    # --------------------------------------------------------

    col3, col4 = st.columns(2)

    with col3:

        craft_style = st.text_input(
            "Craft Style",
            value=product.get(
                "craft_style",
                ""
            ),
            key="catalogue_craft_style"
        )

    with col4:

        category = st.text_input(
            "Category",
            value=product.get(
                "category",
                ""
            ),
            key="catalogue_category"
        )

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = st.text_area(
        "Marketplace Description",
        value=product.get(
            "description",
            ""
        ),
        height=150,
        key="catalogue_description"
    )

    # --------------------------------------------------------
    # TAGS
    # --------------------------------------------------------

    tags = product.get(
        "tags",
        []
    )

    if isinstance(tags, list):
        tags_text = ", ".join(tags)
    else:
        tags_text = str(tags)

    edited_tags = st.text_input(
        "Marketplace Search Tags",
        value=tags_text,
        key="catalogue_tags"
    )

    # --------------------------------------------------------
    # POSSIBLE ORIGIN
    # --------------------------------------------------------

    origin = product.get(
        "possible_origin",
        {}
    )

    if not isinstance(
        origin,
        dict
    ):
        origin = {}

    st.subheader(
        "🌍 Possible Craft Origin"
    )

    origin_col1, origin_col2 = st.columns(2)

    with origin_col1:

        region = origin.get(
            "region",
            "Unknown"
        )

        if not region:
            region = "Unknown"

        st.info(
            f"Region: {region}"
        )

    with origin_col2:

        confidence = origin.get(
            "confidence",
            "low"
        )

        if not confidence:
            confidence = "low"

        st.info(
            f"AI Confidence: {confidence}"
        )

    st.caption(
        "The geographical origin is an AI estimate based "
        "on visible characteristics and should be verified "
        "by the artisan."
    )

    # --------------------------------------------------------
    # STORE EDITED DATA
    # --------------------------------------------------------

    st.session_state.product.update(
        {
            "product_name": product_name,
            "product_type": product_type,
            "material": material,
            "craft_style": craft_style,
            "category": category,
            "description": description,
            "tags": [
                tag.strip()
                for tag in edited_tags.split(",")
                if tag.strip()
            ]
        }
    )


# ============================================================
# STEP 3 - SMART PRICING
# ============================================================

if st.session_state.product is not None:

    st.divider()

    st.markdown(
        '<div class="section-label">STEP 3</div>',
        unsafe_allow_html=True
    )

    st.header(
        "💰 Smart Pricing"
    )

    st.write(
        "Enter the cost of making the product. "
        "KarigarAI will calculate a suggested selling price."
    )

    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:

        material_cost = st.number_input(
            "Material Cost (₹)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            key="material_cost"
        )

        labour_cost = st.number_input(
            "Labour Cost (₹)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            key="labour_cost"
        )

    with cost_col2:

        packaging_cost = st.number_input(
            "Packaging Cost (₹)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            key="packaging_cost"
        )

        other_cost = st.number_input(
            "Other Cost (₹)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            key="other_cost"
        )

    profit_margin = st.slider(
        "Profit Margin (%)",
        min_value=0,
        max_value=100,
        value=30,
        key="profit_margin"
    )

    calculate_button = st.button(
        "💰 Calculate Suggested Price",
        use_container_width=True
    )

    if calculate_button:

        if material_cost <= 0:

            st.warning(
                "Please enter a material cost greater than ₹0."
            )

        else:

            pricing_data = {
                "material_cost": material_cost,
                "labour_cost": labour_cost,
                "packaging_cost": packaging_cost,
                "other_cost": other_cost,
                "profit_margin": profit_margin
            }

            try:

                response = requests.post(
                    f"{API_URL}/suggest-price",
                    json=pricing_data,
                    timeout=30
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state.price_result = (
                        result
                    )

                    st.session_state.product[
                        "price"
                    ] = result[
                        "suggested_price"
                    ]

                    st.success(
                        "Suggested price calculated!"
                    )

                else:

                    st.error(
                        "Pricing calculation failed."
                    )

                    st.code(
                        response.text
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI backend."
                )

            except Exception as error:

                st.error(
                    f"Pricing error: {error}"
                )

    # --------------------------------------------------------
    # DISPLAY PRICE RESULT
    # --------------------------------------------------------

    if st.session_state.price_result is not None:

        result = (
            st.session_state.price_result
        )

        st.subheader(
            "📊 Price Recommendation"
        )

        price_col1, price_col2, price_col3 = (
            st.columns(3)
        )

        with price_col1:

            st.metric(
                "Minimum Price",
                f"₹{result['suggested_min_price']:.2f}"
            )

        with price_col2:

            st.metric(
                "Suggested Price",
                f"₹{result['suggested_price']:.2f}"
            )

        with price_col3:

            st.metric(
                "Maximum Price",
                f"₹{result['suggested_max_price']:.2f}"
            )

        st.markdown(
            f"""
            <div class="price-box">

                <div class="price-heading">
                    Recommended Selling Price
                </div>

                <div class="price-value">
                    ₹{result["suggested_price"]:.2f}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        explanation = result.get(
            "explanation",
            ""
        )

        if explanation:
            st.info(explanation)

    # --------------------------------------------------------
    # FINAL SELLING PRICE
    # --------------------------------------------------------

    current_price = float(
        st.session_state.product.get(
            "price",
            0
        )
        or 0
    )

    final_price = st.number_input(
        "Final Selling Price (₹)",
        min_value=0.0,
        value=current_price,
        step=10.0,
        key="final_selling_price"
    )

    st.session_state.product[
        "price"
    ] = final_price


# ============================================================
# STEP 4 - SAVE / EDIT / APPROVE
# ============================================================

if st.session_state.product is not None:

    st.divider()

    st.markdown(
        '<div class="section-label">STEP 4</div>',
        unsafe_allow_html=True
    )

    st.header(
        "💾 Save & Approve Product"
    )

    st.write(
        "Save the product as a draft, make changes "
        "if required, and approve it when ready."
    )

    action_col1, action_col2, action_col3 = (
        st.columns(3)
    )

    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    with action_col1:

        save_button = st.button(
            "💾 Save Draft",
            use_container_width=True
        )

    with action_col2:

        update_button = st.button(
            "✏️ Save Changes",
            use_container_width=True,
            disabled=(
                st.session_state.product_id
                is None
            )
        )

    with action_col3:

        approve_button = st.button(
            "✅ Approve Product",
            type="primary",
            use_container_width=True,
            disabled=(
                st.session_state.product_id
                is None
            )
        )

    # --------------------------------------------------------
    # PREPARE DATABASE DATA
    # --------------------------------------------------------

    product = st.session_state.product

    product_data = {
        "product_name": product.get(
            "product_name",
            ""
        ),

        "product_type": product.get(
            "product_type",
            ""
        ),

        "material": product.get(
            "material",
            ""
        ),

        "craft_style": product.get(
            "craft_style",
            ""
        ),

        "category": product.get(
            "category",
            ""
        ),

        "description": product.get(
            "description",
            ""
        ),

        "price": float(
            product.get(
                "price",
                0
            )
            or 0
        ),

        "image_filename": (
            st.session_state.filename
        )
    }

    # --------------------------------------------------------
    # SAVE DRAFT
    # --------------------------------------------------------

    if save_button:

        if not product_data[
            "product_name"
        ].strip():

            st.warning(
                "Product name is required."
            )

        else:

            try:

                response = requests.post(
                    f"{API_URL}/products",
                    json=product_data,
                    timeout=30
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.product_id = (
                        data["product_id"]
                    )

                    st.success(
                        "Product saved successfully as Draft! "
                        f"Product ID: {data['product_id']}"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Could not save product."
                    )

                    st.code(
                        response.text
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "FastAPI backend is not running."
                )

            except Exception as error:

                st.error(
                    f"Save error: {error}"
                )

    # --------------------------------------------------------
    # SAVE CHANGES
    # --------------------------------------------------------

    if update_button:

        product_id = (
            st.session_state.product_id
        )

        try:

            response = requests.put(
                f"{API_URL}/products/{product_id}",
                json=product_data,
                timeout=30
            )

            if response.status_code == 200:

                st.success(
                    "Product changes saved successfully!"
                )

            else:

                st.error(
                    "Could not update product."
                )

                st.code(
                    response.text
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "FastAPI backend is not running."
            )

        except Exception as error:

            st.error(
                f"Update error: {error}"
            )

    # --------------------------------------------------------
    # APPROVE PRODUCT
    # --------------------------------------------------------

    if approve_button:

        product_id = (
            st.session_state.product_id
        )

        try:

            response = requests.put(
                f"{API_URL}/products/"
                f"{product_id}/approve",
                timeout=30
            )

            if response.status_code == 200:

                st.success(
                    "🎉 Product approved successfully!"
                )

                st.balloons()

            else:

                st.error(
                    "Could not approve product."
                )

                st.code(
                    response.text
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "FastAPI backend is not running."
            )

        except Exception as error:

            st.error(
                f"Approval error: {error}"
            )

    # --------------------------------------------------------
    # CURRENT PRODUCT
    # --------------------------------------------------------

    if st.session_state.product_id is not None:

        st.info(
            "Current Product ID: "
            f"{st.session_state.product_id}"
        )


# ============================================================
# STEP 5 - PRODUCT DASHBOARD
# ============================================================

st.divider()

st.markdown(
    '<div class="section-label">STEP 5</div>',
    unsafe_allow_html=True
)

st.header(
    "📦 Product Dashboard"
)

st.write(
    "View all products stored in your "
    "artisan marketplace catalogue."
)


# ============================================================
# LOAD PRODUCTS BUTTON
# ============================================================

load_products = st.button(
    "🔄 Load Products",
    use_container_width=True
)


if load_products:

    try:

        response = requests.get(
            f"{API_URL}/products",
            timeout=30
        )

        if response.status_code == 200:

            st.session_state.dashboard_products = (
                response.json()
            )

        else:

            st.error(
                "Could not load products."
            )

            st.code(
                response.text
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "FastAPI backend is not running."
        )

    except Exception as error:

        st.error(
            f"Dashboard error: {error}"
        )


# ============================================================
# DISPLAY PRODUCT DASHBOARD
# ============================================================

if st.session_state.dashboard_products is not None:

    products = (
        st.session_state.dashboard_products
    )

    if len(products) == 0:

        st.info(
            "No products have been saved yet."
        )

    else:

        st.write(
            f"### {len(products)} Product(s)"
        )

        for item in products:

            with st.container(
                border=True
            ):

                product_col, price_col = (
                    st.columns(
                        [3, 1]
                    )
                )

                # --------------------------------------------
                # PRODUCT INFORMATION
                # --------------------------------------------

                with product_col:

                    st.subheader(
                        item.get(
                            "product_name",
                            "Unnamed Product"
                        )
                    )

                    description_text = item.get(
                        "description",
                        ""
                    )

                    if description_text:
                        st.write(
                            description_text
                        )

                    st.write(
                        "**Product Type:**",
                        item.get(
                            "product_type",
                            ""
                        )
                    )

                    st.write(
                        "**Material:**",
                        item.get(
                            "material",
                            ""
                        )
                    )

                    st.write(
                        "**Craft Style:**",
                        item.get(
                            "craft_style",
                            ""
                        )
                    )

                    st.write(
                        "**Category:**",
                        item.get(
                            "category",
                            ""
                        )
                    )

                # --------------------------------------------
                # PRICE + STATUS
                # --------------------------------------------

                with price_col:

                    st.metric(
                        "Selling Price",
                        f"₹{item.get('price', 0)}"
                    )

                    status = item.get(
                        "status",
                        "draft"
                    )

                    if status == "approved":

                        st.success(
                            "✅ APPROVED"
                        )

                    else:

                        st.warning(
                            "📝 DRAFT"
                        )

                    st.caption(
                        "Product ID: "
                        f"{item.get('id')}"
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "KarigarAI • AI-powered catalogue and pricing "
    "assistant for artisans"
)

# ============================================================
# STEP 6 - MARKETPLACE PUBLISHER
# ============================================================

if (
    st.session_state.product is not None
    and st.session_state.product_id is not None
):

    st.divider()

    st.markdown(
        '<div class="section-label">STEP 6</div>',
        unsafe_allow_html=True
    )

    st.header("🌐 Marketplace Publisher")

    st.write(
        "Prepare your approved artisan product for publishing "
        "on online marketplaces."
    )

    # --------------------------------------------------------
    # MARKETPLACE SELECTION
    # --------------------------------------------------------

    marketplace = st.selectbox(
        "Select Marketplace",
        [
            "Amazon",
            "Flipkart"
        ]
    )

    # --------------------------------------------------------
    # SELLER INFORMATION
    # --------------------------------------------------------

    st.subheader("🏪 Seller Information")

    seller_col1, seller_col2 = st.columns(2)

    with seller_col1:

        brand_name = st.text_input(
            "Brand / Artisan Name",
            placeholder="Example: Bundelkhand Crafts"
        )

        sku = st.text_input(
            "Seller SKU",
            value=f"KARIGAR-{st.session_state.product_id:04d}"
        )

    with seller_col2:

        quantity = st.number_input(
            "Available Quantity",
            min_value=1,
            value=1,
            step=1
        )

        manufacturer = st.text_input(
            "Manufacturer / Artisan",
            placeholder="Artisan or workshop name"
        )

    # --------------------------------------------------------
    # PRODUCT DIMENSIONS
    # --------------------------------------------------------

    st.subheader("📦 Product Dimensions")

    dimension_col1, dimension_col2 = st.columns(2)

    with dimension_col1:

        weight = st.number_input(
            "Weight (kg)",
            min_value=0.01,
            value=0.50,
            step=0.10
        )

        length = st.number_input(
            "Length (cm)",
            min_value=0.1,
            value=10.0,
            step=1.0
        )

    with dimension_col2:

        width = st.number_input(
            "Width (cm)",
            min_value=0.1,
            value=10.0,
            step=1.0
        )

        height = st.number_input(
            "Height (cm)",
            min_value=0.1,
            value=10.0,
            step=1.0
        )

    # --------------------------------------------------------
    # PRODUCT CONDITION
    # --------------------------------------------------------

    condition = st.selectbox(
        "Product Condition",
        [
            "New"
        ]
    )

    
       # ============================================================
# STEP 6 - PREPARE MARKETPLACE LISTING
# ============================================================

st.divider()

st.markdown(
    '<div class="section-label">STEP 6</div>',
    unsafe_allow_html=True
)

st.header("🌐 Prepare Marketplace Listing")

st.write(
    "Prepare your product catalogue for Amazon, "
    "Flipkart or another online marketplace."
)


# ------------------------------------------------------------
# CHECK IF PRODUCT EXISTS
# ------------------------------------------------------------

if st.session_state.product is None:

    st.info(
        "First upload and analyze a product in Step 1."
    )

else:

    product = st.session_state.product

    # --------------------------------------------------------
    # SELECT MARKETPLACE
    # --------------------------------------------------------

    marketplace = st.selectbox(
        "Select Marketplace",
        [
            "Amazon",
            "Flipkart"
        ],
        key="marketplace_selection"
    )


    # --------------------------------------------------------
    # SELLER DETAILS
    # --------------------------------------------------------

    st.subheader("🏪 Seller Details")

    brand_name = st.text_input(
        "Brand / Artisan Name",
        placeholder="Example: Bundelkhand Crafts",
        key="marketplace_brand"
    )


    # --------------------------------------------------------
    # SKU
    # --------------------------------------------------------

    if st.session_state.product_id is not None:

        default_sku = (
            f"KARIGAR-{st.session_state.product_id:04d}"
        )

    else:

        default_sku = "KARIGAR-001"


    sku = st.text_input(
        "Product SKU",
        value=default_sku,
        key="marketplace_sku"
    )


    # --------------------------------------------------------
    # STOCK
    # --------------------------------------------------------

    quantity = st.number_input(
        "Available Quantity",
        min_value=1,
        value=1,
        step=1,
        key="marketplace_quantity"
    )


    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    st.subheader("📦 Product Details")

    col1, col2 = st.columns(2)


    with col1:

        weight = st.number_input(
            "Weight (kg)",
            min_value=0.01,
            value=0.50,
            step=0.10,
            key="marketplace_weight"
        )

        length = st.number_input(
            "Length (cm)",
            min_value=0.1,
            value=10.0,
            step=1.0,
            key="marketplace_length"
        )


    with col2:

        width = st.number_input(
            "Width (cm)",
            min_value=0.1,
            value=10.0,
            step=1.0,
            key="marketplace_width"
        )

        height = st.number_input(
            "Height (cm)",
            min_value=0.1,
            value=10.0,
            step=1.0,
            key="marketplace_height"
        )


    # --------------------------------------------------------
    # PREPARE BUTTON
    # --------------------------------------------------------

    prepare_button = st.button(
        "🚀 Prepare Marketplace Listing",
        type="primary",
        use_container_width=True
    )


    # --------------------------------------------------------
    # CREATE MARKETPLACE LISTING
    # --------------------------------------------------------

    if prepare_button:

        if not brand_name.strip():

            st.warning(
                "Please enter your Brand / Artisan Name."
            )

        else:

            # Get tags generated by AI

            tags = product.get(
                "tags",
                []
            )

            if isinstance(tags, list):

                search_terms = ", ".join(tags)

            else:

                search_terms = str(tags)


            # Build marketplace listing

            marketplace_listing = {

                "marketplace":
                    marketplace,

                "sku":
                    sku,

                "title":
                    product.get(
                        "product_name",
                        ""
                    ),

                "brand":
                    brand_name,

                "product_type":
                    product.get(
                        "product_type",
                        ""
                    ),

                "category":
                    product.get(
                        "category",
                        ""
                    ),

                "material":
                    product.get(
                        "material",
                        ""
                    ),

                "description":
                    product.get(
                        "description",
                        ""
                    ),

                "price":
                    product.get(
                        "price",
                        0
                    ),

                "quantity":
                    quantity,

                "search_terms":
                    search_terms,

                "weight_kg":
                    weight,

                "length_cm":
                    length,

                "width_cm":
                    width,

                "height_cm":
                    height,

                "image_filename":
                    st.session_state.filename
            }


            # ------------------------------------------------
            # SUCCESS MESSAGE
            # ------------------------------------------------

            st.success(
                f"✅ {marketplace} listing prepared!"
            )


            # ------------------------------------------------
            # LISTING PREVIEW
            # ------------------------------------------------

            st.subheader(
                f"🛍️ {marketplace} Listing Preview"
            )


            st.markdown(
                f"### {marketplace_listing['title']}"
            )


            st.write(
                marketplace_listing[
                    "description"
                ]
            )


            preview_col1, preview_col2 = (
                st.columns(2)
            )


            with preview_col1:

                st.write(
                    "**Brand:**",
                    marketplace_listing[
                        "brand"
                    ]
                )

                st.write(
                    "**Category:**",
                    marketplace_listing[
                        "category"
                    ]
                )

                st.write(
                    "**Material:**",
                    marketplace_listing[
                        "material"
                    ]
                )

                st.write(
                    "**SKU:**",
                    marketplace_listing[
                        "sku"
                    ]
                )


            with preview_col2:

                st.metric(
                    "Selling Price",
                    f"₹{marketplace_listing['price']}"
                )

                st.metric(
                    "Available Quantity",
                    marketplace_listing[
                        "quantity"
                    ]
                )


            # ------------------------------------------------
            # MARKETPLACE DATA
            # ------------------------------------------------

            with st.expander(
                "🔧 View Marketplace Data"
            ):

                st.json(
                    marketplace_listing
                )


            st.warning(
                "This prepares the listing data only. "
                "It has NOT been published to the real "
                "Amazon or Flipkart marketplace yet."
            )