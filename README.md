# GTHackathon

README.md
H-002 | Hyper-Personalized Customer Support Agent
Problem Statement

Build an AI customer support agent that gives hyper-personalized, context-aware responses based on:

Customer history (loyalty, favorites, coupons)

User’s location (near a store)

Internal knowledge (store timings, offers, policies)

Privacy rules (must mask PII before using LLM)

Example:
User: “I’m cold.”
Bot: “Come inside Starbucks MG Road, it’s warm here! You also have a 10% Hot Cocoa coupon.”

Approach

Customer Profile:
Predefined user info (name, loyalty type, favorite items, coupons, home store).

PII Masking:
Emails + phone numbers are masked as [SENSITIVE] before being sent to the LLM.

RAG (Retrieval Augmented Generation):
Small internal “PDF-like” documents stored as text (store timings, offers, refund policy, etc.).
Simple keyword-based search selects the most relevant info.

LLM Response Generation:
Masked user message + customer profile + RAG documents are sent to the OpenAI model to generate a personalized, specific answer.

Frontend Chat UI:
Simple interface (HTML/CSS/JS) with a location dropdown and chat window.

Backend API:
FastAPI endpoint /chat handles:
→ PII masking
→ Profile lookup
→ RAG retrieval
→ LLM generation

Tools & Technologies

Backend: Python, FastAPI, Uvicorn, OpenAI API, dotenv

Frontend: HTML, CSS, JavaScript

Other: RAG (custom), Regex-based PII masking

Folder Structure
Personalised-bot/
│
├── backend/
│   ├── main.py
│   ├── .env
│
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js

How to Run
1. Backend
cd backend
..\venv\Scripts\activate
uvicorn main:app --reload


Open docs:
http://127.0.0.1:8000/docs

2. Frontend

Open:

frontend/index.html

Key Features

Hyper-personalized replies

RAG-based information retrieval

PII masking for safe LLM usage

Location-aware responses

Simple and clean chat interface
