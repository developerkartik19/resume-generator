# 📄 AI Resume Builder Chatbot

A full-stack web application that collects user information through a conversational interface and generates a professional, ATS-friendly resume using OpenAI GPT (or a built-in template if no API key is available).

---

## 🗂️ Project Structure

```
ai-resume-builder/
│
├── backend/                    ← Python Flask API
│   ├── app.py                  ← Main Flask app, API routes
│   ├── conversation.py         ← Step-by-step Q&A logic
│   ├── resume_generator.py     ← AI resume generation (OpenAI + fallback)
│   ├── requirements.txt        ← Python dependencies
│   └── .env.example            ← Environment variable template
│
├── frontend/
│   └── index.html              ← Complete frontend (HTML + CSS + JS)
│
├── render.yaml                 ← Render deployment config
├── .gitignore
└── README.md
```

---

## ⚡ How to Run Locally

### Step 1: Clone the project
```bash
git clone https://github.com/your-username/ai-resume-builder.git
cd ai-resume-builder
```

### Step 2: Set up the Python backend
```bash
cd backend

# Create a virtual environment (keeps packages isolated)
python -m venv venv

# Activate it:
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure environment variables
```bash
# Copy the example file
cp .env.example .env

# Open .env and add your OpenAI API key (optional — app works without it)
# OPENAI_API_KEY=sk-your-key-here
```

### Step 4: Run the Flask backend
```bash
python app.py
```
You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 5: Open the frontend
Open `frontend/index.html` directly in your browser.
Or use VS Code's Live Server extension.

> **Important**: The frontend's `BACKEND_URL` variable in `index.html` is already
> set to `http://localhost:5000` for local development. No changes needed.

---

## 🧠 How It Works — Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                      (index.html)                           │
│                                                             │
│   User types answer → JavaScript fetch() → POST /chat      │
│                                             ↓               │
│   Bot displays reply  ←  JSON response  ←  Flask           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
│                                                             │
│   app.py          → Receives request, manages session       │
│   conversation.py → Decides which question to ask next      │
│   resume_gen.py   → Calls OpenAI API or uses template       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       OPENAI API                            │
│                                                             │
│   System prompt: "You are an expert resume writer..."       │
│   User prompt:   All collected data                         │
│   Response:      Formatted professional resume              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment

### Backend → Render (Free Tier)
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Add `OPENAI_API_KEY` in Environment Variables

### Frontend → Netlify (Free)
1. Go to [netlify.com](https://netlify.com) → Add new site → Deploy manually
2. Drag and drop the `frontend/` folder
3. **Update `BACKEND_URL`** in `index.html` to your Render URL:
   ```javascript
   const BACKEND_URL = 'https://your-app-name.onrender.com';
   ```

---

## 📝 Example Generated Resume

```
══════════════════════════════════════════════════════════════════════
                           JANE DOE
══════════════════════════════════════════════════════════════════════
  jane@email.com | +1-555-0199  |  San Francisco, USA
  linkedin.com/in/janedoe
──────────────────────────────────────────────────────────────────────

PROFESSIONAL SUMMARY
────────────────────────────────────────────────────────────────
  Full-stack developer with 2 years of experience building scalable
  web applications. Passionate about clean code and user experience.

TECHNICAL SKILLS
────────────────────────────────────────────────────────────────
  Python • React • Flask • PostgreSQL • AWS • Docker • Git

WORK EXPERIENCE
────────────────────────────────────────────────────────────────
  • Software Engineer at TechCorp (2022–2024)
    – Developed RESTful APIs serving 50,000+ daily requests
    – Led migration from monolith to microservices, reducing latency by 40%

PROJECTS
────────────────────────────────────────────────────────────────
  • AI Resume Builder – Python/Flask/OpenAI – Chatbot that auto-generates
    professional resumes from conversational input

EDUCATION
────────────────────────────────────────────────────────────────
  B.S. Computer Science, Stanford University, 2018–2022

ACHIEVEMENTS & CERTIFICATIONS
────────────────────────────────────────────────────────────────
  • AWS Certified Developer – Associate
  • Hackathon Winner – HackSF 2023

══════════════════════════════════════════════════════════════════════
```

---

## 🔑 Getting an OpenAI API Key (Optional)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up / Log in
3. Go to API Keys → Create new secret key
4. Copy it and paste into your `.env` file
5. Note: GPT-3.5-turbo costs roughly $0.002 per resume generated

The app works perfectly **without** an API key using the built-in template!

---

## 📚 Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | HTML/CSS/JavaScript | No build step, deploys anywhere |
| Styling | CSS Custom Properties | Easy theming, no framework needed |
| Backend | Python Flask | Lightweight, easy to learn |
| AI | OpenAI GPT-3.5 | Best-in-class text generation |
| Hosting (API) | Render | Free tier, auto-deploys from GitHub |
| Hosting (UI) | Netlify | Free, instant CDN deployment |
