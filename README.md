# CareerAura

## Prerequisites

- **Python** < 3.2  
- **virtualenv** (since `venv` is not available in Python < 3.3)  
- **Node.js** 18+ and **npm** 9+  
- **Git**

---

## Quick Start

### (1) Backend (local)


# from repo root
cd backend

# create & activate virtualenv
virtualenv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate    # Windows (cmd)
venv\Scripts\activate.ps1  # Windows (PowerShell)

# install dependencies
pip install -r requirements.txt

# configure env vars
cp .env.example .env
then edit .env with your local secrets (see below)

# run server
python app.py

# open a NEW terminal at repo root
cd frontend

# install deps
npm install

# configure env vars
cp .env.example .env
then edit .env to point to your backend, e.g. VITE_API_BASE_URL=http://127.0.0.1:5000

# start dev server
npm run dev


# create backend/.env

use this format:

FLASK_ENV=development
SECRET_KEY=change-me

FRONTEND_ORIGIN=http://localhost:5173

FIREBASE_PROJECT_ID="sap-ai-nonsense"

FIREBASE_GOOGLE_CREDENTIALS="./secrets/serviceAccountKey.json"

GOOGLE_APPLICATION_CREDENTIALS= "./secrets/serviceAccountKey.json"

OPENAI_API_KEY = 


GEMENI_GOOGLE_CREDENTIALS=./secrets/gemeniKey.json


# create backend/secrets

add serviceAccountKey.json from the firebase service
add gemeniKey.json from google 

# create frontend/.env

VITE_BACKEND_API=http://localhost:5000
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=sap-ai-nonsense.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=sap-ai-nonsense
VITE_FIREBASE_STORAGE_BUCKET=sap-ai-nonsense.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=



