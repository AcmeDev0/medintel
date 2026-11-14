# MedIntel AI — Regulatory Intelligence for African Healthcare

Navigate NAFDAC. Ship Compliant. Go to Market Faster.

The only AI-powered regulatory intelligence platform purpose-built for Nigerian and African medical device & drug compliance.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Ingest knowledge base documents
python -m app.ingest

# 5. Run the server
python main.py
```

Visit `http://localhost:8000` to access MedIntel AI.

## Features (MVP)
- 🤖 **Intel Chat** — RAG-powered Q&A grounded in NAFDAC, FDA, WHO regulations
- 📋 **Compliance Checklists** — Step-by-step registration workflows
- 🔍 **Device Classification** — AI-powered medical device class suggestion
- 📄 **Source Citations** — Every answer backed by verifiable regulatory sources

## Tech Stack
- **Backend**: Python + FastAPI
- **AI**: Google Gemini API + LangChain
- **Vector Store**: ChromaDB
- **Frontend**: Jinja2 + Vanilla JS + CSS

## License
Proprietary — AcmeDev
