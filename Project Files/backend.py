from contextlib import asynccontextmanager
from unittest import result
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    initialize_database,
    get_products,
    get_product,
    create_order
)

from ai import ask_ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="ShopMind AI",
    description="AI-powered ecommerce backend",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AIRequest(BaseModel):
    question: str

class OrderRequest(BaseModel):
    customer_name: str
    product_id: int
    quantity: int

@app.get("/")
def home():
    return{
        "status": "success",
        "message": "ShopMind AI backend is running"
    }

@app.get("/products")
def products():
    return get_products()

@app.get("/products/{product_id}")
def product(product_id: int):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/orders")
def order(request: OrderRequest):
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    if not request.customer_name.strip():
        raise HTTPException(status_code=400, detail="Customer name cannot be empty")

    try:
        result = create_order(
            customer_name=request.customer_name,
            product_id=request.product_id,
            quantity=request.quantity
        )
        return{
            "success": True,
            "message": "Order created successfully",
            **result
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.post("/ai")
def ai(request: AIRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    # get current products from the database
    products = get_products()
    #convert product information into AI content 
    product_context = "\n".join(
        [
            (
                f"ID: {product['id']} | "
                f"Name: {product['name']} | "
                f"Category: {product['category']} | "
                f"Price: ₹{product['price']} | "
                f"Description: {product['description']} | "
                f"Stock: {product['stock']}"
            )
            for product in products
        ]
    )

    # Send Ecommerce context to AI layer
    prompt = f"""
You are ShopMind AI, an ecommerce shopping assistant.

Your job is to help customers discover and compare
products available in our store.

IMPORTANT RULES:

1. Only recommend products that exist in the database.
2. Never invent products.
3. Use the actual prices provided.
4. Mention stock availability when relevant.
5. If the customer asks for a recommendation,
   explain why you selected the product.
6. If the customer asks something unrelated to
   ecommerce, politely explain that you specialize
   in shopping assistance.

AVAILABLE PRODUCTS:

{product_context}


CUSTOMER QUESTION:

{request.question}


Provide a clear and helpful response."""

    try:
        result = ask_ai(prompt)
        return {
            "success": True,
            "answer": result["answer"],
            "model": result["model"],
            "route": result["route"]
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(error)}")
