# Intelligent-E-Commerce-Product-Discovery-Shopping-Assistant
# 🛍️ ShopMind AI

An AI-powered e-commerce shopping assistant that helps users discover products, ask questions, and make smarter purchasing decisions.

ShopMind AI combines a FastAPI backend, SQLite database, Streamlit interface, and Cerebras-powered LLM to create an intelligent product discovery experience.

---

## 🚀 Features

- 🤖 AI-powered shopping assistant
- 🔎 Product search and discovery
- 🛍️ Product browsing
- 📦 Product details
- 💬 Natural-language product queries
- ⚡ Cerebras LLM integration
- 🚀 FastAPI REST API
- 🗄️ SQLite database
- 🎨 Streamlit interactive frontend
- 🔗 Backend API integration
- 🔐 Environment-based API key management

---

## 🧠 Example Queries

Users can ask questions such as:

- What is the price of NovaBook Pro?
- Which laptop is best for students?
- Show me products under ₹50,000.
- Compare NovaBook Pro and NovaBook Air.
- Which headphones should I buy?

---

## 🏗️ Architecture

```text
                ┌─────────────────────┐
                │    Streamlit UI     │
                │     app.py          │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │      FastAPI        │
                │    backend.py       │
                └───────┬─────┬───────┘
                        │     │
             ┌──────────┘     └──────────┐
             ▼                           ▼
     ┌───────────────┐          ┌────────────────┐
     │ SQLite DB     │          │  AI Engine     │
     │ database.py   │          │    ai.py       │
     └───────────────┘          └───────┬────────┘
                                        │
                                        ▼
                                ┌────────────────┐
                                │ Cerebras LLM   │
                                └────────────────┘
