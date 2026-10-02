# ============================================================
# ARTISAN AI PRODUCT ENGINE
# ============================================================

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)

import base64
import json
import os
import shutil
import uuid


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Artisan AI Product Engine",
    description=(
        "AI-powered artisan product identification, "
        "catalogue generation and pricing system"
    ),
    version="1.0"
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_FOLDER = Path("uploads")

UPLOAD_FOLDER.mkdir(
    exist_ok=True
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = "sqlite:///./artisan.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ============================================================
# DATABASE PRODUCT MODEL
# ============================================================

class ProductDB(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_name = Column(
        String,
        nullable=False
    )

    product_type = Column(String)

    material = Column(String)

    craft_style = Column(String)

    category = Column(String)

    description = Column(Text)

    price = Column(
        Float,
        default=0
    )

    image_filename = Column(String)

    status = Column(
        String,
        default="draft"
    )


# Create database tables
Base.metadata.create_all(
    bind=engine
)


# ============================================================
# PRODUCT CREATE MODEL
# ============================================================

class ProductCreate(BaseModel):

    product_name: str

    product_type: Optional[str] = ""

    material: Optional[str] = ""

    craft_style: Optional[str] = ""

    category: Optional[str] = ""

    description: Optional[str] = ""

    price: float = 0

    image_filename: Optional[str] = ""


# ============================================================
# PRODUCT UPDATE MODEL
# ============================================================

class ProductUpdate(BaseModel):

    product_name: Optional[str] = None

    product_type: Optional[str] = None

    material: Optional[str] = None

    craft_style: Optional[str] = None

    category: Optional[str] = None

    description: Optional[str] = None

    price: Optional[float] = None

    image_filename: Optional[str] = None


# ============================================================
# PRICING MODEL
# ============================================================

class PricingInput(BaseModel):

    material_cost: float = Field(
        gt=0
    )

    labour_cost: float = Field(
        ge=0
    )

    packaging_cost: float = Field(
        ge=0
    )

    other_cost: float = Field(
        default=0,
        ge=0
    )

    profit_margin: float = Field(
        default=30,
        ge=0,
        le=500
    )


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Artisan AI Product Engine is running!"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# IMAGE TO BASE64
# ============================================================

def image_to_data_url(
    image_path: Path,
    content_type: str
):

    with open(
        image_path,
        "rb"
    ) as image_file:

        encoded_image = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    return (
        f"data:{content_type};"
        f"base64,{encoded_image}"
    )


# ============================================================
# AI PRODUCT ANALYSIS FUNCTION
# ============================================================

def analyze_product(
    image_path: Path,
    content_type: str
):

    image_data = image_to_data_url(
        image_path,
        content_type
    )

    prompt = """
You are an AI assistant for an Indian artisan marketplace.

Analyze the main product visible in the uploaded image.

Return ONLY valid JSON.

Use exactly this structure:

{
    "product_name": "",
    "product_type": "",
    "material": [],
    "craft_style": "",
    "category": "",
    "description": "",
    "tags": [],
    "possible_origin": {
        "region": "",
        "confidence": ""
    }
}

Instructions:

1. Identify the main product.

2. Generate a professional marketplace product name.

3. Identify visible or reasonably likely materials.

4. Identify the craft style only when supported by
visual evidence.

5. Select an appropriate marketplace category.

6. Generate a professional catalogue description.

7. Generate useful marketplace search tags.

8. Do not invent an exact geographical origin.

9. If origin cannot reasonably be determined,
return "Unknown".

10. Origin confidence must be:
"low", "medium", or "high".

11. Do not return Markdown.

12. Return JSON only.
"""

    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        messages=[
            {
                "role": "user",

                "content": [

                    {
                        "type": "text",
                        "text": prompt
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ],

        response_format={
            "type": "json_object"
        },

        temperature=0.2,

        max_completion_tokens=1200
    )

    result = (
        response
        .choices[0]
        .message
        .content
    )

    return json.loads(result)


# ============================================================
# UPLOAD IMAGE + AI PRODUCT ANALYSIS
# ============================================================

@app.post("/analyze-product")
async def analyze_uploaded_product(
    file: UploadFile = File(...)
):

    allowed_types = {

        "image/jpeg": ".jpg",

        "image/png": ".png",

        "image/webp": ".webp"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Upload JPG, PNG or WEBP image."
        )

    extension = allowed_types[
        file.content_type
    ]

    filename = (
        f"{uuid.uuid4()}{extension}"
    )

    file_path = (
        UPLOAD_FOLDER / filename
    )

    try:

        # Save uploaded image
        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # Analyze image using AI
        product_data = analyze_product(
            file_path,
            file.content_type
        )

        return {

            "success": True,

            "filename": filename,

            "product": product_data
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"AI analysis failed: "
                f"{str(error)}"
            )
        )


# ============================================================
# PRICE SUGGESTION
# ============================================================

@app.post("/suggest-price")
def suggest_price(
    data: PricingInput
):

    production_cost = (

        data.material_cost

        + data.labour_cost

        + data.packaging_cost

        + data.other_cost
    )

    suggested_price = (

        production_cost

        * (
            1
            + data.profit_margin / 100
        )
    )

    minimum_price = (
        suggested_price * 0.90
    )

    maximum_price = (
        suggested_price * 1.15
    )

    return {

        "currency": "INR",

        "cost_breakdown": {

            "material_cost":
                round(data.material_cost, 2),

            "labour_cost":
                round(data.labour_cost, 2),

            "packaging_cost":
                round(data.packaging_cost, 2),

            "other_cost":
                round(data.other_cost, 2)
        },

        "production_cost":
            round(production_cost, 2),

        "profit_margin_percent":
            data.profit_margin,

        "suggested_min_price":
            round(minimum_price, 2),

        "suggested_price":
            round(suggested_price, 2),

        "suggested_max_price":
            round(maximum_price, 2),

        "explanation": (
            f"The estimated production cost is "
            f"₹{production_cost:.2f}. "
            f"With a {data.profit_margin:.0f}% margin, "
            f"the suggested selling price is "
            f"₹{suggested_price:.2f}."
        )
    }


# ============================================================
# SAVE PRODUCT AS DRAFT
# ============================================================

@app.post("/products")
def create_product(
    product: ProductCreate
):

    db = SessionLocal()

    try:

        new_product = ProductDB(

            product_name=
                product.product_name,

            product_type=
                product.product_type,

            material=
                product.material,

            craft_style=
                product.craft_style,

            category=
                product.category,

            description=
                product.description,

            price=
                product.price,

            image_filename=
                product.image_filename,

            status="draft"
        )

        db.add(new_product)

        db.commit()

        db.refresh(new_product)

        return {

            "message":
                "Product saved successfully",

            "product_id":
                new_product.id,

            "product_name":
                new_product.product_name,

            "status":
                new_product.status
        }

    finally:

        db.close()


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@app.get("/products")
def get_products():

    db = SessionLocal()

    try:

        products = (
            db.query(ProductDB)
            .all()
        )

        return [

            {

                "id":
                    product.id,

                "product_name":
                    product.product_name,

                "product_type":
                    product.product_type,

                "material":
                    product.material,

                "craft_style":
                    product.craft_style,

                "category":
                    product.category,

                "description":
                    product.description,

                "price":
                    product.price,

                "image_filename":
                    product.image_filename,

                "status":
                    product.status
            }

            for product in products
        ]

    finally:

        db.close()


# ============================================================
# GET SINGLE PRODUCT
# ============================================================

@app.get("/products/{product_id}")
def get_product(
    product_id: int
):

    db = SessionLocal()

    try:

        product = (

            db.query(ProductDB)

            .filter(
                ProductDB.id
                == product_id
            )

            .first()
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return {

            "id":
                product.id,

            "product_name":
                product.product_name,

            "product_type":
                product.product_type,

            "material":
                product.material,

            "craft_style":
                product.craft_style,

            "category":
                product.category,

            "description":
                product.description,

            "price":
                product.price,

            "image_filename":
                product.image_filename,

            "status":
                product.status
        }

    finally:

        db.close()


# ============================================================
# EDIT / CUSTOMIZE PRODUCT
# ============================================================

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    updated_data: ProductUpdate
):

    db = SessionLocal()

    try:

        product = (

            db.query(ProductDB)

            .filter(
                ProductDB.id
                == product_id
            )

            .first()
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # Only fields supplied by the user
        # will be changed
        update_values = (
            updated_data.model_dump(
                exclude_unset=True
            )
        )

        for field, value in update_values.items():

            setattr(
                product,
                field,
                value
            )

        db.commit()

        db.refresh(product)

        return {

            "message":
                "Product updated successfully",

            "product": {

                "id":
                    product.id,

                "product_name":
                    product.product_name,

                "product_type":
                    product.product_type,

                "material":
                    product.material,

                "craft_style":
                    product.craft_style,

                "category":
                    product.category,

                "description":
                    product.description,

                "price":
                    product.price,

                "image_filename":
                    product.image_filename,

                "status":
                    product.status
            }
        }

    finally:

        db.close()


# ============================================================
# APPROVE PRODUCT
# ============================================================

@app.put("/products/{product_id}/approve")
def approve_product(
    product_id: int
):

    db = SessionLocal()

    try:

        product = (

            db.query(ProductDB)

            .filter(
                ProductDB.id
                == product_id
            )

            .first()
        )

        if not product:

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        product.status = "approved"

        db.commit()

        db.refresh(product)

        return {

            "message":
                "Product approved successfully",

            "product_id":
                product.id,

            "product_name":
                product.product_name,

            "status":
                product.status
        }

    finally:

        db.close()