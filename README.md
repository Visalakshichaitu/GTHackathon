H-002 | Hyper-Personalized Customer Support Agent
🚀 Built for the Customer Experience Automation track

🔍 Problem Statement

Retail customers expect instant, specific answers (store timings, stock availability, offers, order status). Traditional chatbots provide generic responses and fail to personalize based on user context.

🎯 Goal

Build an AI support agent that uses:
• Customer history
• Real-time location context
• Internal company knowledge (RAG)
• Privacy-safe processing (PII masking)
to give hyper-personalized and actionable support responses.

💡 Example

User: “I’m cold.”
Bot: “You’re right outside Starbucks MG Road. Come in where it’s warm! You also have a 10% Hot Cocoa coupon today.”

⚙️ Approach

🔹 Customer Profile Personalization:
Includes name, loyalty tier, favorite items, coupons, and order history — used to tailor replies.

🔹 PII Masking:
Phone numbers and emails are automatically masked as [SENSITIVE] before sending the text to the LLM.

🔹 RAG (Retrieval Augmented Generation):
Internal “PDF-like” documents (store timings, offers, refund policy, etc.) are stored as text.
A simple keyword-based retrieval picks the most relevant documents for each query.

🔹 LLM Response Generation:
Final prompt = User message (masked) + Location + Customer profile + Retrieved internal docs.
The AI generates a short, helpful, personalized reply.

🔹 Frontend Chat UI:
Simple and clean interface built using HTML, CSS, and JavaScript.

🔹 Backend API (FastAPI):
Handles PII masking, profile lookup, document retrieval, and final LLM response generation via the /chat endpoint.

🧰 Tools & Technologies

🖥️ Backend: Python, FastAPI, Uvicorn, OpenAI API, dotenv
💻 Frontend: HTML, CSS, JavaScript
🧠 Core Logic: Custom RAG, Regex-based PII masking

📁 Folder Structure

Personalised-bot/
├── backend/
│ ├── main.py
│ └── .env
└── frontend/
├── index.html
├── style.css
└── app.js

▶️ How to Run

1️⃣ Backend:
cd backend
..\venv\Scripts\activate
uvicorn main:app --reload
Open API docs → http://127.0.0.1:8000/docs

2️⃣ Frontend:
Open frontend/index.html (recommended: Live Server)

✨ Features

⭐ Hyper-personalized replies based on customer history
⭐ Location-aware suggestions
⭐ RAG-based internal information retrieval
⭐ PII masking for secure AI usage
⭐ Clean and simple chat UI
